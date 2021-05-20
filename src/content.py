import json
from pygame.image import load as image_load
from pygame import Rect

# NOTE: are we going to read in the **entire** json object on initialization??
# yeah, probably, especially if textures are big boy spritesheets and we don't have a lot
texturedatafile = open('../data/resdata/texture-data.json',)
_TEX_DATA = json.load(texturedatafile)['data']
texturedatafile.close()

frameanimdatafile = open('../data/resdata/frameanim-data.json',)
_FA_DATA = json.load(frameanimdatafile)['data']
frameanimdatafile.close()

''' # NOTE: 

	Since self.loaded will be an array of different struct types for 
	TextureManager and AnimationManager, the only way they could 
	share a parent class like ContentManager is if self.loaded
	were a void* array.
	Eventually, loaded will be split into a handful of arrays (caches) that 
	can be loaded separately into memory, for textures that have
	different frequency of use, for example.

'''

class ContentManager:
	def __init__(self):
		self.content_name_dict = {}
		self.num_loaded = 0
		self.loaded = []	

	def get_contentindex(self, contentid):
		result = -1
		if (contentid in self.content_name_dict):
			fileindex = self.content_name_dict[contentid]
			result = fileindex
		else:
			# load the content from the file
			new_content = self.load(contentid)
			# add the texture/animation/etc to loaded
			self.loaded.append(new_content)
			newcontentindex = self.num_loaded
			self.num_loaded += 1
			# set dict hash for quicker access later 
			# (consider counting usage for smart unloading)
			self.content_name_dict[contentid] = newcontentindex
			result = newcontentindex
		return result

	def load(self, contentid):
		return None

class TextureManager(ContentManager):
	def load(self, textureid):
		# load the full image file (pygame, sdl2, etc)
		filepath = '../%s' % _TEX_DATA[textureid]['filepath']
		new_texture = image_load(filepath)
		new_texture = new_texture.convert() # speeds up blit substantially

		return new_texture

	''' get -> pygame.Surface '''
	# TODO: more sophisticated 'get' using the animation type 
	# (using time on animations, e.g.)?
	def get(self, textureid, framenum_x=0, framenum_y=0):
		textureindex = self.get_contentindex(textureid)
		assert(textureindex != -1) 

		texturedata = _TEX_DATA[textureid]
		frame_dim = (texturedata['frame-width'], texturedata['frame-height'])
		buffer_dim = texturedata['buffer-width'], texturedata['buffer-height']
		frame_offset = (
			framenum_x * (frame_dim[0] + buffer_dim[0]), 
			framenum_y * (frame_dim[1] + buffer_dim[1])
		)
		texture_rect = Rect(frame_offset, frame_dim)

		image = self.loaded[textureindex]
		result = image.subsurface(texture_rect)

		return result

	''' # NOTE: 

		Perhaps after moving code to something more performant (C, C++, Jai ??),
		the data from the JSON will need to be put in a big array of
		some kind, which may necessitate a separate struct for FrameAnimations.
		For now, the sampling function can just live in TextureManager.

	'''

	'''
	def fa_sample(self, animationid, t_percent):
		animationdata = _FA_DATA[animationid]

		textureid = animationdata['textureid']
		framenum_y = animationdata['framenum_y']
		start_x = animationdata['start_x']
		length = animationdata['length']

		framenum_x = int(length * t_percent) + start_x

		result = self.get(textureid, framenum_x=framenum_x, framenum_y=framenum_y)
		return result
	'''

	def fa_timed_sample(self, animationid, ms_since_start, repeat=False):
		animationdata = _FA_DATA[animationid]

		textureid = animationdata['textureid']
		framenum_y = animationdata['framenum_y']
		start_x = animationdata['start_x']
		length = animationdata['length']

		t_percent = 0
		time_ms = animationdata['time_ms']
		if (ms_since_start > time_ms):
			if (repeat):
				t_percent = (ms_since_start % time_ms) / time_ms
			else:
				t_percent = 1.0
		else:
			t_percent = ms_since_start / time_ms

		framenum_x = int(length * t_percent) + start_x

		result = self.get(textureid, framenum_x=framenum_x, framenum_y=framenum_y)
		return result


class BoneAnimationManager(ContentManager):
	def load(self, animationid):
		new_animation
		return new_animation

	def ba_sample(self, animationid, t_percent):
		pass

def test_setup():
	from pygame import init
	from pygame.locals import DOUBLEBUF
	from pygame.display import set_mode
	init()

	# Set the width and height of the screen (width, height).
	screendim = (1024, 720) #use this value when move to C++
	flags = DOUBLEBUF
	window = set_mode(screendim, flags)
	window.set_alpha(None)