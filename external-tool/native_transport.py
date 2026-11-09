"""Materialize generic workshop risers using the measured native lift template."""
import copy,math,time
from blueprint_dimensions import dimensions,volume_cm
from native_assembly import rotate
from native_factory import q,aset

def can_repair(project):
    try:
        flows=project['flows'];inputs=flows['inputs'];outputs=flows['outputs'];rate=outputs[0]['rate']
        recipes={o.get('recipe')for o in project['objects']if o.get('recipe')}
        return len(inputs)==len(outputs)==1 and inputs[0]['id'] in ['Desc_OreIron_C','Desc_IronIngot_C'] and outputs[0]['id']=='Desc_IronPlateReinforced_C' and isinstance(rate,(int,float)) and not isinstance(rate,bool) and math.isfinite(rate) and .2<=rate<=10 and abs(inputs[0]['rate']-rate*12)<1e-6 and recipes<= {'Recipe_IngotIron_C','Recipe_IronPlate_C','Recipe_IronRod_C','Recipe_Screw_C','Recipe_IronPlateReinforced_C'}
    except (KeyError,TypeError,IndexError,AttributeError):return False

def repair(project):
    import native_compact as c,native_project as p
    if not can_repair(project):raise p.ExportError(['La conversion automatique prend en charge fer ou lingots de fer vers plaques renforcées. Les autres plans utilisent le routage générique.'])
    result=c.proposal(dict(inputItem=project['flows']['inputs'][0]['id'],outputRate=project['flows']['outputs'][0]['rate'],size=project['size'],depth=project.get('depth',project['size']),height=project.get('height',project['size']),layoutStyle='compact',pitch='minimum',floorProfile=project.get('floors',[{}])[-1].get('profile','factory'),beltPolicy='auto'))
    for key in ['id','name','appearance','design','buffer']:
        if key in project:result[key]=copy.deepcopy(project[key])
    result.get('design',{}).pop('living',None)
    material=project.get('structure',{}).get('material','concrete');result['structure']['material']=material
    for floor in result['floors']:floor['material']=material
    entry=result['layoutInfo']['input'];output=result['layoutInfo']['output']
    for side,info,item,rate in [('input',entry,result['flows']['inputs'][0]['id'],result['flows']['inputs'][0]['rate']),('output',output,result['flows']['outputs'][0]['id'],result['flows']['outputs'][0]['rate'])]:
        next(o for o in result['objects']if o['id']==info['objectId'])['io']={'side':side,'item':item,'rate':rate}
    _,stats=c.build_project(result)
    return result,stats

def prepare(project):
    import native_project as p
    result=copy.deepcopy(project)
    if not isinstance(result,dict):return result
    objects=result.get('objects',[]);links=result.get('links',[])
    lifts={o.get('id'):o for o in objects if isinstance(o,dict) and o.get('type')=='lift'}
    # Explicit lift elements with one incoming/outgoing belt describe the same
    # two-endpoint riser as an edge's `via`; do not invent branching on a lift.
    for oid in lifts:
        incoming=[l for l in links if l.get('to')==oid and l.get('kind')!='power']
        outgoing=[l for l in links if l.get('from')==oid and l.get('kind')!='power']
        if incoming or outgoing:
            if len(incoming)!=1 or len(outgoing)!=1:raise p.ExportError(['Un élévateur doit avoir exactement une entrée et une sortie. Utilisez des répartiteurs/fusions pour les branches.'])
            a,b=incoming[0],outgoing[0]
            if a.get('item') and b.get('item') and a['item']!=b['item']:raise p.ExportError(['Les deux extrémités de l’élévateur transportent des ressources différentes.'])
            joined={**a,'to':b['to'],'via':oid,'capacity':min(a.get('capacity',result.get('beltCapacity',120)),b.get('capacity',result.get('beltCapacity',120)))}
            if b.get('item'):joined['item']=b['item']
            if b.get('rate',0)>joined.get('rate',0):joined['rate']=b['rate']
            links=[l for l in links if l is not a and l is not b]+[joined]
    by={o.get('id'):o for o in objects if isinstance(o,dict)}
    legacy=bool(lifts) and any(l.get('kind')=='planned' for l in links)
    if legacy:
        for o in objects:
            if o.get('type') in ['splitter','merger'] and o.get('rotation')==0:o['rotation']=180
    for l in links:
        if l.get('kind')=='planned' and lifts:
            a,b=by.get(l.get('from'),{}),by.get(l.get('to'),{})
            if a.get('z',0)!=b.get('z',0) and l.get('via') not in lifts:continue
            if l.get('item') and l.get('rate',0)>0:l['kind']='belt'
    result['links']=links
    return result

def lift(a,position,end_z,in_angle,out_angle,tier,assets):
    import native_project as p
    if not 200<=abs(end_z-position[2])<=4800:raise ValueError('La hauteur d’un élévateur natif doit être comprise entre 2 et 48 m.')
    actor=a.clone(p.load('native-vertical-template.json')['lift'],position,q(in_angle+180))
    aset(actor,'mTopTransform',[[['Rotation',q(out_angle-in_angle-180)],['Translation',[0.,0.,end_z-position[2]]]], [['Rotation','StructProperty',0,'Quat',None,0],['Translation','StructProperty',0,'Vector',None,0]]],['StructProperty',0,'Transform',None,0])
    actor[0].typePath=assets['Build_ConveyorLiftMk'+str(tier)+'_C']['path']
    aset(actor,'mBuiltWithRecipe',p.ref(assets['Recipe_ConveyorLiftMk'+str(tier)+'_C']['path']),['ObjectProperty',0])
    return actor

def crossing(start,end,forward,arrival,boxes,source,target,size,occupied,shaft):
    import native_project as p
    width,depth,height=volume_cm(size)
    preferred=[shaft['x']*100-width/2,shaft['y']*100-depth/2]
    candidates=[preferred]
    # A reserved shaft can describe several separate lanes. Each exported lane
    # gets two distinct native connection components, never a shared lift port.
    for radius in range(200,int(max(width,depth)),200):
        for dx,dy in [(0,radius),(0,-radius),(radius,0),(-radius,0),(radius,radius),(-radius,radius),(radius,-radius),(-radius,-radius)]:candidates.append([preferred[0]+dx,preferred[1]+dy])
    last='Aucun emplacement libre pour l’élévateur.'
    deadline=time.monotonic()+1.5
    for x,y in candidates[:32]:
        if time.monotonic()>deadline:break
        if abs(x)>width/2-65 or abs(y)>depth/2-65:continue
        lo,hi=sorted([start[2],end[2]])
        box=([x-60,y-60,lo-25],[x+60,y+60,hi+25])
        if lo<25 or hi>height-25 or hi-lo<200:continue
        if any(all(min(box[1][j],b1[j])-max(box[0][j],b0[j])>1 for j in range(3))for b0,b1 in boxes.values()):continue
        if any(lo-40<pt[2]<hi+40 and math.hypot(x-pt[0],y-pt[1])<100 for pts in occupied.values()for pt in pts):continue
        temp={**boxes,'@lift':box}
        for entry in [0,90,180,270]:
            direction=[math.cos(math.radians(entry)),math.sin(math.radians(entry)),0]
            try:first=p.route(start,[x,y,start[2]],forward,direction,temp,source,'@lift',size,occupied)
            except ValueError as e:last=str(e);continue
            local={k:list(v)for k,v in occupied.items()}
            for pt in p.samples(first):local.setdefault(tuple(math.floor(v/50)for v in pt),[]).append(pt)
            for exit in [0,90,180,270]:
                outgoing=[math.cos(math.radians(exit)),math.sin(math.radians(exit)),0]
                try:second=p.route([x,y,end[2]],end,outgoing,arrival,temp,'@lift',target,size,local)
                except ValueError as e:last=str(e);continue
                return first,second,[x,y,start[2]],entry,exit,box
    raise ValueError('Élévateur : '+last)

def floor_holes(project,columns):
    # Lifts may clip through a continuous deck; do not reserve whole 8 m tiles.
    return [dict(f,holes=[])for f in copy.deepcopy(project.get('floors',[]))]


def bridge(start,end,forward,arrival,boxes,source,target,size,occupied,project):
    deadline=time.monotonic()+16
    last=None
    for rise in [0,100,200,400,600,800]:
        budget=6 if abs(start[2]-end[2])>.1 else 2
        try:return _bridge(start,end,forward,arrival,boxes,source,target,size,occupied,project,rise,min(deadline,time.monotonic()+budget))
        except ValueError as exc:
            if last is None or 'Pas de hauteur libre' not in str(exc):last=exc
        if time.monotonic()>deadline:break
    raise last

def _bridge(start,end,forward,arrival,boxes,source,target,size,occupied,project,rise,deadline):
    """An overhead service lane leaves the real machine ports unobstructed.

    Each end gets its own riser; a third riser crosses storeys if required.
    Nothing may pass through a hard building envelope or an existing belt.
    """
    import native_project as p
    width,depth,height=volume_cm(size)
    levels=sorted(f['z']*100 for f in project.get('floors',[])) or [0]
    def rail(point):
        base=max(z for z in levels if z<=point[2]);ceiling=next((z for z in levels if z>point[2]),height)
        top=max([point[2]]+[hi[2]for oid,(lo,hi)in boxes.items() if not oid.startswith('@') and lo[2]>=base and lo[2]<ceiling])
        if project.get('design',{}).get('enabled') and project.get('design',{}).get('family')=='m05':ceiling=min(ceiling,3060)
        z=400 if project.get('nativeProfile')=='clean-manifold-v1'else (point[2]+200 if project.get('generation',{}).get('layoutPolicy')=='subzones-v1' else max(top+50,point[2]+200))+rise
        if z+25>=ceiling:raise ValueError('Pas de hauteur libre pour une voie logistique au-dessus des machines.')
        return z
    sr,tr=rail(start),rail(end)
    def heads(point,direction,z,reverse=False):
        for distance in range(125,1001,25):
            xy=[point[i]+direction[i]*distance*(-1 if reverse else 1) for i in [0,1]]
            if any(abs(v)>[width,depth][i]/2-65 for i,v in enumerate(xy)):continue
            lo,hi=sorted([point[2],z]);column=([xy[0]-60,xy[1]-60,lo-25],[xy[0]+60,xy[1]+60,hi+25])
            if any(all(min(column[1][j],b1[j])-max(column[0][j],b0[j])>1 for j in range(3))for b0,b1 in boxes.values()):continue
            if any(lo-40<pt[2]<hi+40 and math.hypot(xy[0]-pt[0],xy[1]-pt[1])<100 for pts in occupied.values()for pt in pts):continue
            yield xy,column
    def angle(v):return round(math.degrees(math.atan2(v[1],v[0])))%360
    sh=list(heads(start,forward,sr));th=list(heads(end,arrival,tr,True))
    for (sx,sy),sc in sh:
        if time.monotonic()>deadline:break
        temp={**boxes,'@sourceHead':sc}
        try:first=p.route(start,[sx,sy,start[2]],forward,forward,temp,source,'@sourceHead',size,occupied)
        except ValueError:continue
        first_occupied={k:list(v)for k,v in occupied.items()}
        for pt in p.samples(first):first_occupied.setdefault(tuple(math.floor(v/50)for v in pt),[]).append(pt)
        for (tx,ty),tc in th:
            if all(min(sc[1][j],tc[1][j])-max(sc[0][j],tc[0][j])>1 for j in range(3)):continue
            temp2={**temp,'@targetHead':tc}
            try:last=p.route([tx,ty,end[2]],end,arrival,arrival,temp2,'@targetHead',target,size,first_occupied)
            except ValueError:continue
            lane_occupied={k:list(v)for k,v in first_occupied.items()}
            for pt in p.samples(last):lane_occupied.setdefault(tuple(math.floor(v/50)for v in pt),[]).append(pt)
            preferred=angle([tx-sx,ty-sy,0]);preferred=(round(preferred/90)*90)%360
            directions=[preferred,(preferred+90)%360,(preferred+270)%360,(preferred+180)%360]
            for sa in directions:
                sd=[math.cos(math.radians(sa)),math.sin(math.radians(sa)),0]
                for ta in directions:
                    if time.monotonic()>deadline:raise ValueError('Recherche de voie supérieure limitée ; dégagez les ports ou espacez les machines.')
                    td=[math.cos(math.radians(ta)),math.sin(math.radians(ta)),0]
                    try:
                        if abs(sr-tr)<.1:
                            middle=p.route([sx,sy,sr],[tx,ty,tr],sd,td,temp2,'@sourceHead','@targetHead',size,lane_occupied)
                            risers=[([sx,sy,start[2]],sr,angle(forward),sa,sc),([tx,ty,tr],end[2],ta,angle(arrival),tc)]
                            return [first,middle,last],risers
                        via={'x':max(2,min(project['size']-2,((sx+tx)/2+width/2)/100)),'y':max(2,min(project.get('depth',project['size'])-2,((sy+ty)/2+depth/2)/100))}
                        cross=crossing([sx,sy,sr],[tx,ty,tr],sd,td,temp2,'@sourceHead','@targetHead',size,lane_occupied,via)
                        aa,bb,pos,entry,exit,col=cross
                        risers=[([sx,sy,start[2]],sr,angle(forward),sa,sc),(pos,tr,entry,exit,col),([tx,ty,tr],end[2],ta,angle(arrival),tc)]
                        return [first,aa,bb,last],risers
                    except ValueError:continue
    raise ValueError('Aucune voie logistique supérieure ne peut relier ces ports sans collision.')


