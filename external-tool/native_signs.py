"""Experimental native luminous signs, encoded with explicit sign properties.

Property names/layout paths cross-checked against SC-InteractiveMap Building/Sign.js.
Binary read-back is required; visual emission remains an in-game validation boundary.
"""
import math
def add(assembly,part,project,assets):
 import native_project as p
 from native_factory import aset
 from native_assembly import rotate
 if part['asset']not in['StandaloneWidgetSign_Portrait','StandaloneWidgetSign_SmallVeryWide']or part.get('emission')not in[0,1,2,3]:raise p.ExportError(['Panneau lumineux non pris en charge.'])
 position=[(part['x']-project['size']/2)*100,(part['y']-project.get('depth',project['size'])/2)*100,part['z']*100]
 angle=math.radians(part['rotation']-90)/2
 actor=assembly.clone(p.load('native-design-template.json')['piece'],position,part.get('nativeSignQuaternion')or[0,0,math.sin(angle),math.cos(angle)])
 stem=part['asset'];actor[0].typePath=assets['Build_'+stem+'_C']['path'];aset(actor,'mBuiltWithRecipe',p.ref(assets['Recipe_'+stem+'_C']['path']),['ObjectProperty',0])
 p.paint(actor,part['color']);rgb=[int(part['color'][i:i+2],16)/255 for i in [1,3,5]];linear=[v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in rgb]+[1.]
 for key in ['mBackgroundColor','mForegroundColor','mAuxilaryColor']:aset(actor,key,linear,['StructProperty',0,'LinearColor',None,0])
 aset(actor,'mEmissive',float(part['emission']),['FloatProperty',0]);aset(actor,'mGlossiness',0.,['FloatProperty',0])
 layout='/Game/FactoryGame/Interface/UI/InGame/Signs/SignLayouts/BPW_Sign2x3_0.BPW_Sign2x3_0_C'
 if stem=='StandaloneWidgetSign_SmallVeryWide':layout='/Game/FactoryGame/Interface/UI/InGame/Signs/SignLayouts/BPW_Sign4x1_2.BPW_Sign4x1_2_C'
 aset(actor,'mActivePrefabLayout',p.ref(layout),['ObjectProperty',0])
 # The parser represents a soft path as two strings plus a trailing uint32.
 base,sub=layout.rsplit('.',1)
 import native_blueprint as n
 aset(actor,'mSoftActivePrefabLayout',[n.sav_parse.ObjectReference(base,sub),0],['SoftObjectProperty',0])
 return actor
