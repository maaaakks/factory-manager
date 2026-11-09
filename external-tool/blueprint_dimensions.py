"""Independent plot bounds, in metres; legacy `size` remains the X dimension."""
MAX_DIMENSION=512
def dimensions(project):
 width=project.get('size',48);depth=project.get('depth',width);height=project.get('height',width)
 if any(type(v)is not int or not 8<=v<=MAX_DIMENSION or v%8 for v in [width,depth,height]):raise ValueError('Dimensions libres : multiples de 8 m, entre 8 et 512 m par axe.')
 return width,depth,height
def volume_cm(value):
 return tuple(value)if isinstance(value,(list,tuple))else(value,value,value)
def header_dimensions(project):
 dims=tuple(v//8 for v in dimensions(project))
 return dims[0]if len(set(dims))==1 else list(dims)
def experimental(project):
 w,d,h=dimensions(project)
 return w!=d or w!=h or w not in[32,40,48]
