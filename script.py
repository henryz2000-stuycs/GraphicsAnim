import mdl
from display import *
from matrix import *
from draw import *

basename = "default"
is_anim = False
num_frames = 1
knobs = []

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):
    global basename
    global is_anim
    global num_frames
    
    found_basename = False
    found_frames = False
    
    for command in commands:
        op = command["op"]
        args = command["args"]
        
        if op == "frames":
            found_frames = True
            num_frames = args[0]
            is_anim = True
            
            if not found_basename:
                print "Setting basename to '" + basename + "'"
                
        elif op == "basename":
            is_anim = True
            found_basename = True
            basename = args[0]
            
        elif op == "vary":
            is_anim = True
            
            if not found_frames:
                print "Must call 'frames' command before calling vary"
                return
            
            if args[0] > num_frames-1 \
              or args[0] < 0 \
              or args[1] > num_frames-1 \
              or args[1] < 0:
              
              print "Vary range out of bounds"
              return

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    global knobs
    
    for i in range(int(num_frames)):
        knobs.append({})
        
    for command in commands:
        op = command["op"]
        args = command["args"]
        
        if op == "vary":
            knob = command["knob"]
            start_frame = args[0]
            end_frame = args[1]
            start_val = args[2]
            end_val = args[3]
            increment = (end_val - start_val) / (end_frame - start_frame)
            current = start_val
            
            for i in range(int(start_frame), int(end_frame) + 1):
                if i == end_frame:
                    current = end_val
                knobs[i][knob] = current
                current += increment

def run(filename):
    """
    This function runs an mdl script
    """
    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [0,
              255,
              255]]
    areflect = [0.1,
                0.1,
                0.1]
    dreflect = [0.5,
                0.5,
                0.5]
    sreflect = [0.5,
                0.5,
                0.5]

    color = [0, 0, 0]
    tmp = new_matrix()
    ident( tmp )

    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 20
    consts = ''
    coords = []
    coords1 = []

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    first_pass(commands)
    second_pass(commands, num_frames)

    print "Basename: " + basename
    print "Num Frames: " + str(num_frames)

    for frame in range(int(num_frames)):
        print "Frame #: " + str(frame)

        for knob in knobs[frame]:
            symbols[knob][1] = knobs[frame][knob]

        for command in commands:
            c = command["op"]
            args = command["args"]
            if args != None:
                args = command["args"][:]

            if args != None \
                and "knob" in command \
                and command["knob"] != None \
                and c in ["move", "scale", "rotate"]:
                
                knob = command["knob"]
                
                for i in range(len(args)):
                    if not isinstance(args[i], basestring):
                        args[i] *= symbols[knob][1]

            if c == 'box':
                if isinstance(args[0], str):
                    consts = args[0]
                    args = args[1:]
                if isinstance(args[-1], str):
                    coords = args[-1]
                add_box(tmp, args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp, args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
                tmp = []
            elif c == 'torus':
                add_torus(tmp, args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
                tmp = []
            elif c == 'line':
                if isinstance(args[0], str):
                    consts = args[0]
                    args = args[1:]
                if isinstance(args[3], str):
                    coords = args[3]
                    args = args[:3] + args[4:]
                if isinstance(args[-1], str):
                    coords1 = args[-1]
                add_edge(tmp, args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
                
        if is_anim:
            save_extension(screen, ("./anim/" + basename + ("%03d" % frame) + ".png"))
            
        tmp = new_matrix()
        ident( tmp )
        
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 20

    if is_anim:
        make_animation(basename)
                        
