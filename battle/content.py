import json
from pygame.image import load as image_load
from pygame import Rect

texturedatafile = open('../data/resdata/texture-data.json',)
TEX_DATA = json.load(texturedatafile)['textures']
texturedatafile.close()

class ContentLoader:
	def __init__(self):
		self.content_name_dict = {}
		self.num_loaded = 0
		self.loaded = []	

	def get_contentindex(self, contentid, indexinfile=0):
		result = -1
		if (contentid in self.content_name_dict):
			fileindex = self.content_name_dict[contentid]
			result = fileindex + indexinfile
		else:
			# load the content from the file
			new_content, length = self.load(contentid)
			# add the texture/animation/etc to loaded
			assert(length > 0)
			assert(indexinfile < length)
			result = self.num_loaded + indexinfile
			self.loaded += new_content # append all items in new_content to loaded
			self.num_loaded += length
			# set dict hash for quicker access later (consider counting usage for smart unloading)
			self.content_name_dict[contentid] = new_content
		return result

	def load(self, contentid):
		# TODO: override this in child classes
		return ([], 0)

class TextureLoader(ContentLoader):
	def load(self, textureid):
		new_textures = []
		length = 0

		# get info from json
		texturedata = TEX_DATA[textureid]

		# load the full image file (pygame, sdl2, etc)
		filepath = '../%s' % texturedata['filepath']
		parenttexture = image_load(filepath)

		# load each piece of the image file into separate textures, and increment length
		current_offset_x, current_offset_y = 0, 0
		frame_dim = (texturedata['frame-width'], texturedata['frame-height'])

		width, height = texturedata['width'], texturedata['height']
		length += width * height

		buffer_dim = texturedata['buffer-width'], texturedata['buffer-height']

		for j in range(height):
			current_offset_y = j * frame_dim[1] + buffer_dim[1]
			for i in range(width):
				current_offset_x = i * frame_dim[0] + buffer_dim[0]
				current_offset = (current_offset_x, current_offset_y)
				text_rect = Rect(current_offset, frame_dim)
				new_textures.append(parenttexture.subsurface(text_rect))

		return (new_textures, length)

class AnimationLoader(ContentLoader):
	def load(self, animationid):
		new_animations = []
		length = 0
		return (new_animations, length)