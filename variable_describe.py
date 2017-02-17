## Describing Variables 
#
# as dict, str or HTML
#
### Helper functions to deal with annotated variables

import numpy as np

plotting_possible = False
plotting_exceptions = []
do_3d_plot = True
try:
    import matplotlib
    import matplotlib.pylab as plt
    from IPython.core import pylabtools as pt
    gui, backend = pt.find_gui_and_backend('inline', 'inline')
    from IPython.core.pylabtools import activate_matplotlib
    activate_matplotlib(backend)
    plotting_possible = True
except Exception as e:
    plotting_exceptions.append(e)
    pass

def describe(v,**kwargs):
    return _Descriptor(v,**kwargs)

class _Descriptor(object):
    def __init__(self,v,**kwargs):
        self.v = v
        self.kwargs = kwargs
    def __repr__(self):
        return repr(describe_dict(self.v))
    def __str__(self):
        return str(describe_dict(self.v))
    def _repr_html_(self):
        return describe_html(self.v,wrap_in_html=False,**self.kwargs)

def describe_dict(v):
    if type(v) in [list, tuple] or hasattr(v,'__iter__'):
        try:
            return [describe_text(vv) for vv in v]
        except:
            # Tensor Variables love to raise TypeErrors when iterated over
            pass
    d = {}
    for k in ['name','simple_name','doc','config_key','optimizable','node','save','init','get','set']:
        if hasattr(v,k):
            d[k] = getattr(v,k)
    try:
        d['value'] = v.get_value()
    except:
        pass
    try:
        d['got'] = v.get(tu.create_context_O(v))
    except:
        pass
    return d

def _plot_to_string():
    import StringIO, urllib
    import base64
    import matplotlib.pylab as plt
    imgdata = StringIO.StringIO()
    plt.savefig(imgdata)
    plt.close()
    imgdata.seek(0) 
    image = base64.encodestring(imgdata.buf)  
    return str(urllib.quote(image))    

def _tensor_to_html(t,title='',figsize=(5,4),line_figsize=(5,1.5),line_kwargs={},imshow_kwargs={},preamble=True,**other_kwargs):
    """
        This function plots/prints numerical objects of 0,1,2,3 and 5 dimensions such that it can be displayed as html.
    """
    kwargs = {'title':title,'figsize':figsize,'line_figsize':line_figsize,'line_kwargs':line_kwargs,'imshow_kwargs':imshow_kwargs}
    imshow_kwargs['interpolation'] = imshow_kwargs.get('interpolation','nearest')
    if type(t) == int or type(t) == float:
        return str(t)
    elif type(t) == np.ndarray:
        if plotting_possible:
            import matplotlib.pylab as plt
            if len(t.shape) == 0:
                return str(t)
            if len(t.shape) == 1:
                if t.shape[0] == 1:
                    if preamble is False:
                        return str(t[0])
                    return str(t[0]) + ' (1,)'
                else:
                    plt.figure(figsize=line_figsize)
                    if title != '':
                        plt.title(title)
                    plt.plot(t,**line_kwargs)
                    plt.tight_layout()
                    if preamble is False:
                        return "<img src='data:image/png;base64," + _plot_to_string() + "'>"
                    return "Numpy array "+str(t.shape)+"<br/><img src='data:image/png;base64," + _plot_to_string() + "'>"
            elif len(t.shape) == 2:
                if t.shape[0] == 1 and t.shape[1] == 1:
                    if preamble is False:
                        return str(t[0])
                    return str(t[0]) + ' (1,1)'
                else:
                    if np.abs(float(t.shape[0] - t.shape[1]))/(t.shape[0]+t.shape[1]) < 0.143:
                        # for roughly square 2d objects
                        plt.figure(figsize=figsize)
                        if title != '':
                            plt.title(title)
                        plt.imshow(t,**imshow_kwargs)
                        plt.colorbar()
                    else:
                        plt.figure(figsize=line_figsize)
                        # for 2d objects with one long side:
                        if t.shape[0] > t.shape[1]:
                            plt.plot(t,**line_kwargs)
                        else:
                            plt.plot(t.transpose(),**line_kwargs)
                    plt.tight_layout()
                    if preamble is False:
                        return "<img src='data:image/png;base64," + _plot_to_string() + "'>"
                    return "Numpy array "+str(t.shape)+"<br/><img src='data:image/png;base64," + _plot_to_string() + "'>"
            elif len(t.shape) == 3:
                if t.shape[0] == 1 and t.shape[1] == 1 and t.shape[2] == 1:
                    return str(t[0]) + ' (1,1,1)'
                else:
                    legend = ""
                    if t.shape[0] == 1:
                        img = _tensor_to_html(t[0,:,:],preamble=False,**kwargs)
                    elif t.shape[1] == 1 and t.shape[2] == 1:
                        img = _tensor_to_html(t[:,0,0],preamble=False,**kwargs)
                    else:
                        ## Todo: Plotting profiles of other dimensions iff they show interesting changes
                        #
                        # Right now the profile is plotted if the tensor is sufficiently small.
                        # But a better way would be to determine if the profile is "interesting"
                        # and then sampling a few lines from there.
                        plt.figure(figsize=figsize)
                        if title != '':
                            plt.suptitle(title)
                        plt.subplot(221)
                        plt.title('mean over time')
                        plt.imshow(t.mean(0),**imshow_kwargs)
                        plt.subplot(222)
                        plt.title('mean over x')
                        if t.shape[2] <= 30:
                            plt.plot(t.mean(0),range(t.shape[1]),'k',alpha=0.2,**line_kwargs)
                            legend += 'Grey lines show the profile of the x dimension. '
                        if t.shape[0] <= 100:
                            plt.plot(t.mean(2).transpose(),range(t.shape[1]),'g',alpha=0.2,**line_kwargs)
                        plt.plot(t.mean((0,2)),range(t.shape[1]),**line_kwargs)
                        plt.gca().invert_yaxis()
                        plt.ylabel('y')
                        plt.subplot(223)
                        plt.title('mean over y')
                        if t.shape[1] <= 30:
                            plt.plot(t.mean(0).transpose(),'r',alpha=0.2,**line_kwargs)
                            legend += 'Red lines show the profile of the y dimension. '
                        if t.shape[0] <= 100:
                            plt.plot(t.mean(1).transpose(),'g',alpha=0.2,**line_kwargs)
                            legend += 'Green lines show different time points. '
                        plt.plot(t.mean((0,1)),**line_kwargs)
                        plt.xlabel('x')
                        plt.subplot(224)
                        plt.title('mean over x and y')
                        if t.shape[1]+t.shape[2] <= 2*30:
                            plt.plot(t.reshape((t.shape[0],-1)),color='orange',alpha=0.1,**line_kwargs)
                            legend += 'Orange lines show the spatial profile over time. '
                        plt.plot(t.mean((1,2)),**line_kwargs)  
                        plt.xlabel('time')
                        plt.tight_layout()
                        img = "<img src='data:image/png;base64," + _plot_to_string() + "'>"

                        if do_3d_plot and t.shape[0] <= 20:
                            # TODO: create config for these cutoff values
                            with OrthographicWrapper():
                                ax = plot_3d_tensor_as_3d_plot(t)
                                plt.tight_layout()
                                img += "<img src='data:image/png;base64," + _plot_to_string() + "'>"
                    if preamble is False:
                        return img
                    return "Numpy array "+str(t.shape)+"<br/>"+img+legend            
            elif len(t.shape) == 5:
                # we assume its actually 3d with extra dimensions
                if t.shape[0] == 1 and t.shape[2] == 1:
                    return "Numpy array "+str(t.shape)+"<br/>"+_tensor_to_html(t[0,:,0,:,:],preamble=False,**kwargs)
                else:
                    return '5D tensor with too large first or third dimensions!'
        return 'Numpy Array ('+str(t.shape)+')'
    else:
        if preamble is False:
            return str(t[0])
        return str(type(t))+': '+str(t)

on_click_toggle =  """onclick='$(this).parent().children(".description_content").toggle();$(this).parent().children(".description_content_replacer").toggle();'"""

var_name_counter = 0

def save_name(n):
    if type(n) != str:
        if hasattr(n,'name'):
            n = n.name
        else:
            try:
                global var_name_counter
                n.name = 'unnamed_var_'+str(var_name_counter)
                n = n.name
                var_name_counter += 1
            except:
                raise Exception('save_name got a '+str(type(n))+' instead of a string or object with name attribute.')
    n = n.replace(' ', '_').replace('-', '_').replace('+', '_').replace('*', '_').replace('&', '_').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
    if n[0] in '0123456789':
        n = 'n'+n
    return n
def full_path(v):
    return '_'.join([save_name(p) for p in getattr(v,'path',[v])])

def describe_html(v,wrap_in_html=True,**kwargs):
    from IPython.display import HTML
    import uuid
    try:
        import html
    except:
        import cgi as html # fallback escape function
    ##       
    # Handeling other datatypes
    #
    if type(v) == int or type(v) == float:
        s = str(v)
        if not wrap_in_html:
            return s
        return HTML(s)
    elif type(v) == np.ndarray:
        s = _tensor_to_html(v,**kwargs)
        if not wrap_in_html:
            return s
        return HTML(s)
    if type(v) in [dict] or hasattr(v,'__iteritems__'):
        uid = uuid.uuid4().hex
        s = "<div class='convis_description list'>"
        iteration = v.__iteritems__() if hasattr(v,'__iteritems__') else v.iteritems()
        s += "<b id="+uid+" "+on_click_toggle+" >+</b>&nbsp;"
        for (k,vv) in v.__iteritems__():
            s += '| <a style="text-decoration: none; font-size: 8pt;" href="#'+uid+save_name(k)+'">'+k+'</a> '
        s += "<div class='description_content_replacer' style='border-left: 4px solid #f0f0f0; border-top: 4px solid #f8f8f8; padding-left: 10px; margin-bottom: 10px; display: none;'>(&#8230;)</div>"
        s += "<div class='description_content' style='border-left: 4px solid #f0f0f0; border-top: 4px solid #f8f8f8; padding-left: 10px; margin-bottom: 10px;'>"
        iteration = v.__iteritems__() if hasattr(v,'__iteritems__') else v.iteritems()
        for (k,vv) in v.__iteritems__():
            s += "<div class='convis_description dict_item'><b id="+uid+save_name(k)+" "+on_click_toggle+" >"+str(k)+"</b> <a style=\"text-decoration: none;\" href='#"+uid+"''>&#8617;</a>"
            s += "<div class='description_content_replacer' style='border-left: 0px solid #ddd; padding-left: 5px; display: none;'>(&#8230;)</div>"
            s += "<div class='description_content' style='border-left: 0px solid #ddd; padding-left: 5px;'>"
            s += describe_html(vv,wrap_in_html=False,**kwargs)
            s += "</div>"
            s += "</div>"
        s += "</div>"
        s += "</div>"
        if not wrap_in_html:
            return s
        return HTML(s)
    if type(v) in [list, tuple] or hasattr(v,'__iter__'):
        try:
            s = "<div class='convis_description list'><b "+on_click_toggle+">List ("+str(len(v))+"):</b>"
            s += "<div class='description_content_replacer' style='border-left: 4px solid #f0f0f0; border-top: 4px solid #f8f8f8; padding-left: 10px; margin-bottom: 10px; display: none;'>(&#8230;)</div>"
            s += "<div class='description_content' style='border-left: 4px solid #f0f0f0; border-top: 4px solid #f8f8f8; padding-left: 10px; margin-bottom: 10px;'>"
            s += '\n'.join([describe_html(vv,wrap_in_html=False,**kwargs) for vv in v])
            s += "</div>"
            s += "</div>"
            if not wrap_in_html:
                return s
            return HTML(s)
        except:
            # Tensor Variables love to raise TypeErrors when iterated over
            pass
    ##       
    # Assuming its a annotated theano variable:
    #
    d = {}
    for k in ['name','simple_name','doc','config_key','optimizable','node','save','init','get','set','variable_type']:
        if hasattr(v,k):
            d[k] = getattr(v,k)
    name = d.get('name','') # optional: None handling
    if not type(name) is str or name is '':
        name= repr(v)
    if hasattr(v,'html_name'):
        name+=' '+str(v.html_name)
    #simple_name = str(d.get('simple_name',''))
    s = """<div class='convis_description variable'><b """+on_click_toggle+""">"""+name+"""</b> <small>"""+d.get('variable_type','')+"""</small>"""
    # default: show everything, hide on click;
    s += "<div class='description_content_replacer' style='border-left: 2px solid #eee; padding-left: 5px; margin-bottom: 10px; display: none;'>(&#8230;)</div>"
    s += "<div class='description_content' style='border-left: 2px solid #eee; border-top: 2px solid #f8f8f8;  padding-left: 5px; margin-bottom: 10px;  margin-top: 2px;'>"
    if hasattr(v,'path'):
        s += "<small>" + full_path(v) + "</small><br/>"
    if hasattr(v,'doc') and getattr(v,'doc') != '':
        s += '<p class="doc" style="padding:2px;">'+getattr(v,'doc')+'</p>'
    if hasattr(v,'owner'):
        s += "<tt style='color: gray;'><small>" + str(v.owner) + "</small></tt><br/>"
    for k in ['config_key','optimizable','node','save','init','get','set','state_out_state','param_init','state_init','state_in_state','copied_from','config_key','config_default']:
        if hasattr(v,k):
            s+= '<div><b>'+str(k)+'</b>: <tt>'+html.escape(str(getattr(v,k)))+'</tt></div>'
    try:
        if hasattr(v,'get_value'):
            s+= '<b>value</b>: ' + str(_tensor_to_html(v.get_value(),title=name,**kwargs))
    except Exception as e:
        s+= '<b>value</b>: ' + str(e)
        pass
    try:
        s+= '<b>got</b>: ' + _tensor_to_html(v.get(tu.create_context_O(v)),title=name,**kwargs)
    except:
        pass
    s += """</div>"""
    s += """</div>"""
    if not wrap_in_html:
        return s
    return HTML(s)

class OrthographicWrapper():
    def __init__(self):
        """
            This context manager overwrites the persp_transformation function of proj3d
            to perform orthographic projections.
            Plots that are show()n or save()d in this context will use the projection.

            After the context closes, the old projection is restored.
        """
        pass
    def __enter__(self):
        from mpl_toolkits.mplot3d import proj3d
        def orthogonal_proj(zfront, zback):
            a = (zfront+zback)/(zfront-zback)
            b = -2*(zfront*zback)/(zfront-zback)
            # -0.0001 added for numerical stability as suggested in:
            # http://stackoverflow.com/questions/23840756
            return np.array([[1,0,0,0],
                                [0,1,0,0],
                                [0,0,a,b],
                                [0,0,-0.0001,zback]])
        if not hasattr(proj3d,'old_persp_transformation'):
            proj3d.old_persp_transformation = proj3d.persp_transformation
        proj3d.persp_transformation = orthogonal_proj
    def __exit__(self, eType, eValue, eTrace):
        from mpl_toolkits.mplot3d import proj3d
        plt.show() # we have to show all the plots before restoring the transformation
        if hasattr(proj3d,'old_persp_transformation'):
            proj3d.persp_transformation = proj3d.old_persp_transformation

def plot_3d_tensor_as_3d_plot(ar,ax=None,scale_ar=None,num_levels = 20, contour_cmap='coolwarm_r', contourf_cmap='gray', view=(25, 65)):
    """
        Until I come up with a 3d contour plot that shows the contours of a volume, 
        this function visualizes a sequence of images as contour plots stacked on top of each other.
        The sides of the plot show a projection onto the xz and yz planes (at index 0).

            ar: the array to visualize

            ax: (if available) the matplotlib axis (in projection='3d' mode) from eg. calling subplot
                if none is provided, the current axis will be converted to 3d projection

            scale_ar: the array that is used for scaling (usefull if comparing arrays or visualizing only a small section)

            num_levels: number of levels of contours

            contour_cmap='coolwarm_r': color map used for line contours

            contourf_cmap='gray': color map used for surface contour

            view: tuple of two floats that give the azimuth and angle of the projection


        returns:

            axis that was used for plotting


    """
    from mpl_toolkits.mplot3d import proj3d
    if ax is None:
        ax = plt.gca(projection='3d')
    if scale_ar is None:
        scale_ar = ar
    k_range = 0.5*np.max(scale_ar)-np.min(scale_ar)
    X, Y = np.meshgrid(np.arange(ar.shape[1]), np.arange(ar.shape[2]))
    levels = np.linspace(np.min(scale_ar), np.max(scale_ar), num_levels)
    for i,k in enumerate(ar):
        alpha = 100.0*(np.std(k)+0.003)
        if alpha > 1.0:
            alpha = 1.0
        if alpha < 0.0:
            alpha = 0.0
        k_scale = 1.0
        ax.contourf(X, Y, i+k_scale*k, cmap=contourf_cmap, 
                   levels=i+k_scale*levels,alpha=0.5*alpha)
        ax.contour(X, Y,i-k_scale*k/k_range, cmap=contour_cmap, 
                   levels=i-k_scale*levels/k_range,alpha=1.0,linewidths=3)
        side_line_color = [plt.cm.get_cmap(contour_cmap)(1.0-(np.mean(k)-np.min(scale_ar))/k_range)]
        cset = ax.contour(X, Y, i*np.ones_like(k), zdir='x', offset=0, cmap=None, colors='k',alpha=0.25)
        cset = ax.contour(X, Y, i*np.ones_like(k), zdir='y', offset=0, cmap=None, colors='k',alpha=0.25)
        cset = ax.contour(X, Y, i-k_scale*k/k_range, zdir='x', offset=0, cmap=None, colors=side_line_color,alpha=0.5*alpha)
        cset = ax.contour(X, Y, i-k_scale*k/k_range, zdir='y', offset=0, cmap=None, colors=side_line_color,alpha=0.5*alpha)
    ax.view_init(*view)
    ax.set_zlabel('time')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zticks(range(ar.shape[0]),minor=False)
    ax.invert_zaxis()
    return ax