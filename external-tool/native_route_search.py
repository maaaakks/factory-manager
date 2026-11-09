"""Bounded cardinal search for routes requiring several service-lane turns.

The native spline and collision validator remain authoritative at the caller.
"""
import heapq,math,time

def search(start,end,boxes,occupied,bounds,forward,arrival):
    z=start[2]
    axes=[]
    for j in [0,1]:
        values={round(start[j],4),round(end[j],4)}
        values.update(range(-int(bounds[j]/2)+200,int(bounds[j]/2)-199,200))
        axes.append(sorted(values))
    xs,ys=axes;origin=(xs.index(round(start[0],4)),ys.index(round(start[1],4)));goal=(xs.index(round(end[0],4)),ys.index(round(end[1],4)))
    hard=[(lo,hi)for lo,hi in boxes.values()if lo[2]-.05<=z<=hi[2]+.05]
    nearby={}
    for key,pts in occupied.items():
        if abs(key[2]*50-z)>100:continue
        for pt in pts:
            if abs(pt[2]-z)<50:nearby.setdefault((math.floor(pt[0]/200),math.floor(pt[1]/200)),[]).append(pt)
    cache={}
    def clear(x,y):
        key=(x,y)
        if key in cache:return cache[key]
        ok=not any(lo[0]-110<x<hi[0]+110 and lo[1]-110<y<hi[1]+110 for lo,hi in hard)
        if ok:
            bx,by=math.floor(x/200),math.floor(y/200)
            ok=not any(math.hypot(x-p[0],y-p[1])<125 for dx in [-1,0,1]for dy in [-1,0,1]for p in nearby.get((bx+dx,by+dy),[]))
        cache[key]=ok;return ok
    def distance(ix,iy):return abs(xs[ix]-end[0])+abs(ys[iy]-end[1])
    cardinal=lambda v:round(math.atan2(v[1],v[0])/(math.pi/2))%4
    state=(*origin,cardinal(forward),200);queue=[(distance(*origin),0,state)];cost={state:0};parents={};expanded=0
    while queue and expanded<6000:
        _,g,current=heapq.heappop(queue)
        if g!=cost.get(current):continue
        ix,iy,previous,run=current;expanded+=1
        if (ix,iy)==goal and previous!=(cardinal(arrival)+2)%4 and run>=100:
            result=[]
            while current in parents:
                result.append([xs[current[0]],ys[current[1]],z]);current=parents[current]
            result.append(list(start));return result[::-1]
        for direction,(dx,dy)in enumerate([(1,0),(0,1),(-1,0),(0,-1)]):
            if previous>=0 and (direction==(previous+2)%4 or direction!=previous and run<200):continue
            nx,ny=ix+dx,iy+dy
            if not(0<=nx<len(xs) and 0<=ny<len(ys)):continue
            length=abs(xs[nx]-xs[ix])+abs(ys[ny]-ys[iy]);steps=max(1,math.ceil(length/50))
            if not all(clear(xs[ix]+(xs[nx]-xs[ix])*i/steps,ys[iy]+(ys[ny]-ys[iy])*i/steps)for i in range(1,steps+1)):continue
            step=round(min(200,run+length if previous==direction else length),4);nxt=(nx,ny,direction,step);ng=g+length+(100 if previous>=0 and previous!=direction else 0)
            if ng>=cost.get(nxt,float('inf')):continue
            cost[nxt]=ng;parents[nxt]=current;heapq.heappush(queue,(ng+distance(nx,ny),ng,nxt))
    return None
