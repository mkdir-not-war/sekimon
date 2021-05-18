import json

class ContentLoader:
	def __init__(self):
		self.content_name_dict = {}
		self.num_loaded = 0
		self.loaded = []

		texturedatafile = open('../data/resdata/texture-data.json',)
		self.TEX_DATA = json.load(texturedatafile)['textures']
		texturedatafile.close()

	def get_contentindex(self, contentid, indexinfile=0):
		result = -1
		if (contentid in self.content_name_dict):
			fileindex = self.content_name_dict[contentid]
			result = fileindex + indexinfile
		else:
			# load the content from the file
			new_content, length = self.load_content(contentid)
			# add the texture/animation/etc to loaded
			assert(length > 0)
			assert(indexinfile < length)
			result = self.num_loaded + indexinfile
			self.loaded += new_content # append all items in new_content to loaded
			self.num_loaded += length
			# set dict hash for quicker access later (consider counting usage for smart unloading)
			self.content_name_dict[contentid] = result
		return result

	def load(self, contentid):
		# TODO: override this in child classes
		return ([], 0)

class TextureLoader(ContentLoader):
	def load(self, textureid):
		new_textures = []
		length = 0

		# get info from json
		texturedata = self.TEX_DATA[textureid]

		# load the full image file
		print(texturedata)

		# load each piece of the image file into separate textures, and increment length

		return (new_textures, length)

class AnimationLoader(ContentLoader):
	def load(self, animationid):
		new_animations = []
		length = 0
		return (new_animations, length)