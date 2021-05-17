

class ContentLoader:
	def __init__(self):
		self.content_name_dict = {}
		self.num_loaded = 0
		self.loaded = []

	def get_contentindex(self, filename, indexinfile=0):
		result = -1
		if (filename in self.content_name_dict):
			fileindex = self.content_name_dict[filename]
			result = fileindex + indexinfile
		else:
			# load the content from the file
			new_content, length = self.load_content(filename)
			# add the texture/animation/etc to loaded
			assert(length > 0)
			assert(indexinfile < length)
			result = self.num_loaded + indexinfile
			self.loaded += new_content # append all items in new_content to loaded
			self.num_loaded += length
			# set dict hash for quicker access later (consider counting usage for smart unloading)
			self.content_name_dict[filename] = result
		return result

	def load_content(self, filename):
		# TODO: override this in child classes
		return ([], 0)

class TextureLoader(ContentLoader):
	def load_content(self, filename):
		new_textures = []
		length = 0
		# read json data for textures
		# load the full image file
		# load each piece of the image file into separate textures
		return (new_textures, length)

class AnimationLoader(ContentLoader):
	def load_content(self, filename):
		new_animations = []
		length = 0
		return (new_animations, length)