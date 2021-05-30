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

boneanimdatafile = open('../data/resdata/boneanim-data.json',)
_BA_DATA = json.load(boneanimdatafile)['data']
boneanimdatafile.close()

''' # NOTE: 

	Since self.loaded will be an array of different struct types for 
	TextureManager and AnimationManager, the only way they could 
	share a parent class like ContentManager is if self.loaded
	were a void* array.
	Eventually, loaded will be split into a handful of arrays (caches) that 
	can be loaded separately into memory, for textures that have
	different frequency of use, for example.

'''

###### These methods are only used in the animation editor ##############

editordatafile = open('../data/resdata/animationeditor-data.json',)
_EDIT_DATA = json.load(editordatafile)
editordatafile.close()

_WORKING_BA_DATA = _BA_DATA.copy()

def get_allboneanimids():
	result = list(_WORKING_BA_DATA.keys())
	return result

def get_bonesinanim(animid):
	result = list(_WORKING_BA_DATA[animid]['bones'].keys())
	return result

def get_animationdata(animid):
	# get a complete copy of the data, changes made to this will be reflected in dict
	result = _WORKING_BA_DATA[animid]

def reset_animationdata(animid):
	_WORKING_BA_DATA[animid] = _BA_DATA[animid].copy()
	print("Reset working animation data to current data from json.")

#########################################################################

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

class BoneFrame:
	def __init__(self, visible, x, y, rot):
		self.visible = visible
		self.x = x
		self.y = y
		self.pos = (x, y)
		self.rot = rot

	def print(self):
		print('vis:%s, (%d, %d), @%d deg' % (self.visible, self.x, self.y, self.rot))

class BoneAnimation:
	def __init__(self, name, numframes, numbones):
		self.name = name
		self.numframes = numframes
		self.numbones = numbones
		self.bones = {}

	def set_boneframe(self, bonename, frame, visible, x, y, rot):
		newbf = BoneFrame(visible, x, y, rot)
		self.bones[bonename][frame] = newbf

	def get_final_boneframe(self, bone):
		result = self.bones[bone][self.numframes-1]
		return result

	def lerp_boneframe(self, bone, indexA, indexB, t):
		frameA = self.bones[bone][indexA]
		while (frameA == None):
			indexA -= 1
			frameA = self.bones[bone][indexA]

		frameB = self.bones[bone][indexB]
		while (frameB == None):
			indexB += 1
			frameB = self.bones[bone][indexA]

		rotdiff1 = frameB.rot - frameA.rot
		rotdiff2 = (frameB.rot-360) - frameA.rot
		rotdiff3 = frameB.rot - (frameA.rot-360)

		rotdiff = rotdiff1
		if (abs(rotdiff2) < abs(rotdiff)):
			rotdiff = rotdiff2
		if (abs(rotdiff3) < abs(rotdiff)):
			rotdiff = rotdiff3

		result = BoneFrame(
			frameA.visible,
			frameA.x + t * (frameB.x - frameA.x),
			frameA.y + t * (frameB.y - frameA.y),
			frameA.rot + t * rotdiff
		)

		return result

class BoneAnimationManager(ContentManager):
	def __init__(self, editor=False):
		self.data = None
		if (editor):
			self.data = _WORKING_BA_DATA
		else:
			self.data = _BA_DATA

	def load(self, animationid):
		animdata = self.data[animationid]

		bones = animdata['bones']
		numframes = animdata['num-frames']

		new_animation = BoneAnimation(
			animationid, 
			animdata['num-frames'], 
			animdata['num-bones']
		)

		for bone in bones:
			new_animation.bones[bone] = [None] * new_animation.numframes

			for frame in range(len(bones[bone])):
				framedata = bones[bone][frame]
				if (framedata != None):
					new_animation.set_boneframe(
						bone, 
						frame,
						framedata['visible'],
						framedata['position-x'],
						framedata['position-y'],
						framedata['rotation-deg']
					)

		'''
		For the sake of speed (and since the ContentManager is already space efficient),
		we're going to store all the frames, not just the key frames in the JSON.
		To get the frames in between the key frames, we'll do the lerping up front here.
		'''

		lerpbounds = []
		for bone in bones:
			startindex = 0
			nextindex = 0
			for frame in bones[bone]:
				if (frame == None):
					if (startindex == nextindex):
						startindex -= 1
				else:
					# this frame has data
					if (nextindex > startindex):
						lerpbounds.append((startindex, nextindex))
						# reset start index
						startindex = nextindex
					startindex += 1
				nextindex += 1
			break

		for bounds in lerpbounds:
			start = bounds[0]
			finish = bounds[1]
			diff = finish - start
			current = 1

			assert(current != diff)
			while (current != diff):
				for bone in bones:
					lerpedframe = new_animation.lerp_boneframe(
						bone, start, finish, current/diff
					)
					new_animation.bones[bone][start+current] = lerpedframe
				current += 1

		return new_animation

	def ba_sample(self, animationid, t_percent):
		animindex = self.get_contentindex(animationid)
		assert(animindex != -1)

		animation = self.loaded[animindex]

		# sample the frames using lerp, return a dict of BoneFrames
		result = {}

		if (t_percent >= 1.0):
			for bone in animation.bones:
				ff = animation.get_final_boneframe(bone)
				result[bone] = ff
		else:
			index = int((animation.numframes-1) * t_percent)
			t = (animation.numframes-1) * t_percent - index
			for bone in animation.bones:
				result[bone] = animation.lerp_boneframe(bone, index, index+1, t)

		return result
			


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