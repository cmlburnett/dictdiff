"""
DictDiff -- an interactive dictionary diff class.

Simple class that performs a diff on two dictionaries.
The end result of the diff is a set of instructions neded to be performed to change the dictionaries.
While this may seem excessive, the point is to use the instructions to modify a database.
For example, if two sets of key/value metadata represented as a dictionary were diff'ed
 then this would provide the instructions that could be then performed in a database
 setting to delete, insert, or update rows in the database.
Additionally, the diff is performed in an intereactive manner to permit the user to
 selectively approve or tweak the diff as it is being performed.

There are plenty of enhancements that could be done;
 - Cannot add new keys that are not in the provided dictionaries
 - No type conversions performed on new data
 - Values are assumed to be simple types (int, str, etc.); no nesting supported
"""

__all__ = ['DictDiff']

import textwrap

class DictDiff:
	"""
	Class that handles diff'ing the contents of two dictionaries.
	It performs an interactive editing process with the user to
	 display the differences and permits the user to modify or keep
	 a particular version.
	The end result is a set of "instructions" to permit modification of A into B.
	This is necessary for when the dictionary represents something more than just a dictionary
	 such as rows in a database.

	Final result is a list of tuples containing actions to convert self.A to self.B.
	These tuples consist of (ACTION, KEY, VALUE).
	Known actions are:
		k		Keep original value in self.A
		a		Add a new key/value
		d		Delete a key/value
		e		Edit value for an existing key

	The key is the dictionary key being edited.
	The value is the value that should be used for key, which may be a new value or a
	 modified value or the value that it was prior to being deleted.

	Overall, this returned set of "instructions" permits modification of A into B, with possibility
	 of the user controlling the differences.
	"""

	def __init__(self, a=None,b=None):
		if a == None: a = {}
		if b == None: b = {}

		if type(a) is not dict:
			raise TypeError("First argument, a, is required to be None or a dict, got %s" % (str(type(a)),))
		if type(b) is not dict:
			raise TypeError("Second argument, b, is required to be None or a dict, got %s" % (str(type(b)),))

		self._a = a
		self._b = b

	@property
	def A(self): return self._a

	@property
	def B(self): return self._b


	def AutoDiff(self, title):
		"""
		Accept the differences automatically.
		This shows the differences but does not ask the user for any input.

		Arguments:
			title			Displayed title for this diff operation

		See class description for more information on return value.
		"""
		return self.ShowDiff(title, autoaccept=True)

	def ShowDiff(self, title, autoaccept=False):
		"""
		Interactively asks the user for accepting differences and permits editing.

		Arguments:
			title			Displayed title for this diff operation
			autoaccept		If True then all changes are automically accepted

		See class description for more information on return value.
		"""

		while True:
			ret = self._ShowDiff(title, autoaccept)

			print("Done diffing. Review the following changes:")
			for prop in ret:
				l = prop[0]
				k = prop[1]
				v = prop[2]

				if l == 'a':
					print("\tAdd %s=%s" % (k,v))
				elif l == 'd':
					print("\tDelete %s" % k)
				elif l == 'k':
					print("\tKeep %s=%s" % (k,v))
				elif l == 'e':
					print("\tChange %s to %s" % (k,v))
				else:
					raise KeyError("Unrecognized prop value '%s'" % l)

			while True:
				if autoaccept:
					which = 's'
				else:
					which = input("(S)ave or (r)edo? ")


				if which == 's' or not len(which):
					return ret
				elif which == 'r':
					# Repeat outer while loop
					break
				else:
					print("\tUnrecognized input, try again")
					print("")

	def _ShowDiff(self, title, autoaccept=False):
		"""
		Helper function to actually perform the diff showing.

		See ShowDiff for arguments.

		See class description for more information on return value.
		"""

		# Show the title
		print("{:^110}".format(title))

		# Make the keys a set so builtin set functions can be used
		a_keys = set(self.A.keys())
		b_keys = set(self.B.keys())

		# Nothing to do if there's nothing in the dictionaries
		if len(a_keys) == 0 and len(b_keys) == 0:
			return []

		# The three possibilities: the keys that are common to both, the keys that are new (b_has), and the keys that were deleted (a_has)
		common = sorted(a_keys.intersection(b_keys))
		a_has = sorted(a_keys.difference(b_keys))
		b_has = sorted(b_keys.difference(a_keys))

		# Necessary to know how to format the columns
		maxkeylen = max([len(k) for k in a_keys] + [len(k) for k in b_keys])

		# Return list of operations approved by user for changing A to B
		ret = []

		# Iterate through deleted keys
		for k in a_has:
			zz = DictDiff._ShowRow(k, maxkeylen, self.A[k], "", "Deleted", False, autoaccept)
			if zz != None:
				ret.append(zz)

		# Iterate through new keys
		for k in b_has:
			zz = DictDiff._ShowRow(k, maxkeylen, "", self.B[k], "Added", False, autoaccept)
			if zz != None:
				ret.append(zz)

		# Iterate through kept keys
		for k in common:
			if self.A[k] == self.B[k]:
				status = 'Unchanged'
			else:
				status = 'Different'

			zz = DictDiff._ShowRow(k, maxkeylen, self.A[k], self.B[k], status, False, autoaccept)
			if zz != None:
				ret.append(zz)

		# TODO: one thing not included here is adding in new keys not in A nor B

		print("")

		return ret

	@staticmethod
	def _ShowRow(k, maxkeylen, left, right, status, justprint=False, autoaccept=False):
		"""
		Helper function to show one specific key comparison (deleted, added, unchanged, different).

		Arguments:
			k			The key being compared
			maxkeylen	The maximum key length so taht the column can be formatted to the correct width of other rows
			left		The "original" value of the key @k in self.A
			right		The "new" value of the key @k in self.B
			status		The status of the key ("Deleted", "Added", "Unchanged", "Different")
			justprint	If True, then just print the difference and return 'k' for keep left value.
			autoaccept	If True, accept whatever is different between @left and @right.

		See class description for more information on return value.
		"""

		# Keep a copy of the original values just in case
		orig_left = left
		orig_right = right

		# Convert left and right values to strings
		if left == None:	left = ""
		else:				left = str(left)

		if right == None:	right = ""
		else:				right = str(right)

		# Wrap strings to 40 character widths so they can be appropriately displayed
		lefts = textwrap.wrap(left, 40)
		rights = textwrap.wrap(right, 40)

		# Format two strings for diplaying the differences
		#  s1 consists of "| KEY || LEFT VALUE | RIGHT VALUE || OPERATION |"
		#  s2 consists of "| KEY || LEFT VALUE | RIGHT VALUE ||           |"
		# where
		#  KEY is the dictionary key being operated on
		#  LEFT VALUE is the "original" value in self.A
		#  RIGHT VALUE is the "new" value in self.B
		#  OPERATION is textual description of what's being done ("Deleted", "Added", "Unchanged", "Different") as provided in @status
		s1 = "|%%%ds || %%42s | %%42s || %%%ds |" % (maxkeylen+1,10)
		s2 = ("|%%%ds || %%%%42s | %%%%42s || %%%ds |" % (maxkeylen+1,10)) % (' ',' ')

		# If nothing to show, which happens if textwrap.wrap("") is called as this return [], an empty list
		# So if nothing to show then mark as keep
		if len(lefts) == 0 and len(rights) == 0:
			s = s1 % (k, "", "", status)

			print("-" * len(s))
			print(s)

		else:
			# Shows all lines necessary to display the full value of both @left and @right as wrapped
			# text lines of 40 chars per column
			for i in range(max(len(lefts),len(rights))):
				if i in range(len(lefts)):	left = lefts[i]
				else:						left = None

				if i in range(len(rights)):	right = rights[i]
				else:						right = None

				# Only for first line (i.e., i==0) show the status code (s1)
				# otherwise show the blank space'ed version (s2)
				if i == 0:
					if left and right:
						s = s1 % (k, left, right, status)
					elif left:
						s = s1 % (k, left, "", status)
					elif right:
						s = s1 % (k, "", right, status)
				else:
					if left and right:
						s = s2 % (left, right)
					elif left:
						s = s2 % (left, "")
					elif right:
						s = s2 % ("", right)

				# Show horizontal line that starts the row
				if i == 0:
					print("-" * len(s))
				print(s)

		# If instruction to just print, then keep the original value
		if justprint:
			return ('k', k, left)

		# Iterate until a satisfactory input is received
		while True:
			# If unchanged then query the user to keep, edit, or delete
			if status == 'Unchanged':
				if autoaccept:
					which = 'c'
				else:
					which = input("(C)ontinue unchanged, input (n)ew value, or (d)elete value? ")


				# Continue means to keep the LEFT value
				if which.lower() == 'c' or not len(which):
					return ('k', k, orig_left)

				# New value permits user to enter a new value for this key
				elif which.lower() == 'n':
					val = input("Enter new value: ")
					return ('e', k, val)

				# Delete means to get rid of the LEFT value
				elif which.lower() == 'd':
					return ('d', k, orig_left)

			# If there is a change, then query user about what to do with it
			else:
				# If instructed to accept it then assume a RIGHT selection
				if autoaccept:
					which = 'r'
				else:
					which = input("(L)eft, (r)ight, input (n)ew value, or (d)elete value? ")


				# If the user wants the LEFT value then that depends on the status
				if which.lower() == 'l':
					# If not in RIGHT, then the action is KEEP
					if status == 'Deleted':
						return ('k', k, orig_left)

					# If not in LEFT, then the action is nothing as deleting a new value is equivalent to nothing
					elif status == 'Added':
						return None

					# Otherwise KEEP the left value
					else:
						return ('k', k, orig_left)

				# If the user wants the RIGHT value then that depends on the status
				elif which.lower() == 'r':
					# If not in RIGHT, then the action is DELETE
					if status == 'Deleted':
						return ('d', k, orig_right)

					# If not in LEFT, then the action is ADD
					elif status == 'Added':
						return ('a', k, orig_right)

					# Otherwise EDIT the value to the RIGHT value
					else:
						return ('e', k, orig_right)

				# If the user wants a new value, then query and consider it an EDIT
				elif which.lower() == 'n':
					val = input("Enter new value: ")
					return ('e', k, val)

				# If the user wants to DELETE, then DELETE it
				elif which.lower() == 'd':
					return ('d', k, orig_left)

			print("\tUnrecognized input: enter l or r")

	def WasChanged(self, props):
		"""
		This takes the set of instructions for AutoDiff or ShowDiff and indicates if there were any changes.
		This essentially means knowing if any of the instructions are anything but KEEP.
		"""

		return any([prop[0] != 'k' for prop in props])

	def ApplyDiff(self, src, diff, allowAdd=True, allowDelete=True, allowChange=True, allowKeep=True):
		"""
		Applying the diff.
		This applies the instructions in @diff to dictionary @src.
		Because the interactive nature of ShowDiff, the end result very well could be different from self.B,
		 hence the need for this function to actually carry out the editing on a dictionary.
		One twist is a set of flags that permit the caller to limit the actions as sometimes
		 some of these actions cannot or should not be performed [in the database, etc.].
		Not all of these really make sense, but there's only four actions so might as well permit
		 controlling all four of them with flags.

		Arguments:
			src				Dictionary of source information prior to applying instructions
			diff			List of instructions to perform
			allowAdd		If True then permit ADD instructions
			allowDelete		If True then permit DELETE instructions
			allowChange		If True then permit EDIT instructions
			allowKeep		If True then permit KEEP instructions

		Returned is a dictionary that is @src modified by the @diff instructions based upon
		 the permitted flags.
		"""

		# Copy the source dictionary
		ret = dict(src)

		# Check if there are no changes
		nochange = all([d[0] == 'k' for d in diff])

		if nochange:
			return

		# Apply changes to @a
		for d in diff:
			l = d[0]
			k = d[1]
			v = d[2]

			# Delete property
			if l == 'd':
				if not allowDelete: raise KeyError("Deleting properties is not allowed")
				del ret[k]

			# Add property
			elif l == 'a':
				if not allowAdd: raise KeyError("Adding properties is not allowed")
				ret[k] = v

			# Keep property
			elif l == 'k':
				if not allowKeep: raise KeyError("Keeping properties is not allowed")

				pass

			# Change property
			elif l == 'e':
				if not allowChange: raise KeyError("Changing properties is not allowed")

				ret[k] = v

			else:
				raise KeyError("Unrecognized diff command: %s" % l)

		# Return the dictionary based on @src and modified per @diff instructions
		return ret





if __name__ == '__main__':
	a = {"Alice": 10, "Bob": 20, "Charlie": 30}
	b = {"Alice": 15, "Bob": 20, "David": 40}

	d = DictDiff(a,b)
	res = d.AutoDiff("Test 1")

	# Make sure diff is as expected
	assert type(res) == list
	assert len(res) == 4
	assert type(res[0]) == tuple
	assert type(res[1]) == tuple
	assert type(res[2]) == tuple
	assert type(res[3]) == tuple
	assert len(res[0]) == 3
	assert len(res[1]) == 3
	assert len(res[2]) == 3
	assert len(res[3]) == 3
	assert res[0][0] == 'd'
	assert res[0][1] == 'Charlie'
	assert res[1][0] == 'a'
	assert res[1][1] == 'David'
	assert res[1][2] == 40
	assert res[2][0] == 'e'
	assert res[2][1] == 'Alice'
	assert res[2][2] == 15
	assert res[3][0] == 'k'
	assert res[3][1] == 'Bob'
	assert res[3][2] == 20

	# Make sure result is as expected
	c = d.ApplyDiff(a, res)
	assert type(c) == dict
	assert len(c) == 3
	assert 'Alice' in c
	assert c['Alice'] == 15
	assert 'Bob' in c
	assert c['Bob'] == 20
	assert 'David' in c
	assert c['David'] == 40

	# Make sure original is unchanged
	assert len(a) == 3
	assert 'Charlie' in a
	assert 'David' not in a



	try:
		d.ApplyDiff(a, res, allowDelete=False)
		assert False, "Should not have been permitted"
	except:
		pass

	try:
		d.ApplyDiff(a, res, allowDelete=True)
	except:
		assert False, "Should have been permitted"



	try:
		d.ApplyDiff(a, res, allowAdd=False)
		assert False, "Should not have been permitted"
	except:
		pass

	try:
		d.ApplyDiff(a, res, allowAdd=True)
	except:
		assert False, "Should have been permitted"



	try:
		d.ApplyDiff(a, res, allowChange=False)
		assert False, "Should not have been permitted"
	except:
		pass

	try:
		d.ApplyDiff(a, res, allowChange=True)
	except:
		assert False, "Should have been permitted"



	try:
		d.ApplyDiff(a, res, allowKeep=False)
		assert False, "Should not have been permitted"
	except:
		pass

	try:
		d.ApplyDiff(a, res, allowKeep=True)
	except:
		assert False, "Should have been permitted"


