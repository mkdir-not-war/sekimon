import json
from pygame.image import load as image_load
from pygame import Rect

texturedatafile = open('../data/resdata/texture-data.json',)
TEX_DATA = json.load(texturedatafile)['textures']
texturedatafile.close()

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
			# set dict hash for quicker access later (consider counting usage for smart unloading)
			self.content_name_dict[contentid] = newcontentindex
			result = newcontentindex
		return result

	def load(self, contentid):
		# TODO: override this in child classes
		return ([], 0)

class TextureManager(ContentManager):
	def load(self, textureid):
		# load the full image file (pygame, sdl2, etc)
		filepath = '../%s' % TEX_DATA[textureid]['filepath']
		new_texture = image_load(filepath)

		return new_texture

	''' get -> pygame.Surface '''
	def get(self, textureid, framepos_x=0, framepos_y=0):
		textureindex = self.get_contentindex(textureid)
		assert(textureindex != -1) 

		texturedata = TEX_DATA[textureid]
		frame_dim = (texturedata['frame-width'], texturedata['frame-height'])
		buffer_dim = texturedata['buffer-width'], texturedata['buffer-height']
		frame_offset = (
			framepos_x * (frame_dim[0] + buffer_dim[0]), 
			framepos_y * (frame_dim[1] + buffer_dim[1])
		)
		texture_rect = Rect(frame_offset, frame_dim)

		result = self.loaded[textureindex].subsurface(texture_rect)

		return result

class AnimationManager(ContentManager):
	def load(self, animationid):
		new_animations = []
		length = 0
		return (new_animations, length)