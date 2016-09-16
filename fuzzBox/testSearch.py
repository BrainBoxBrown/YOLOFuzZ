#!/usr/bin/python

def smart_search(my_list, low, high, will_fail=False, need_setup=True):
		"""
			Binary search
			return true if no crash
		"""
		print "Doing {0}->{1}".format(low, high) 
		jmps = my_list[low:high]
		if len(jmps) == 0:
			return 

		print len(jmps)
		if need_setup:
			for jmp in my_list:

				if jmp["valid"] != 0:
					print "rechecking! " + str(my_list.index(jmp))
					jmp["breakpoint"].enabled = False
					continue
				if jmp in jmps:

					if not jmp["breakpoint"].enabled:
						jmp["breakpoint"].enabled = True
				else:
					if jmp["breakpoint"].enabled:
						jmp["breakpoint"].enabled = False

		print len(jmps)
		if will_fail or self.fucked_run():
			# things didn't work
			l = len(jmps)# 16
			if will_fail:
				print "knew it'd be fucked"

			print "Fucked {0}->{1}".format(low, high) 
			if l == 1:
				print jmps[0]
				if will_fail and self.fucked_run():
					print "Accuratly predicted fuckery"
					jmps[0]["valid"] = -1
				else:
					print "FAILED PREDICTION!!!!"
					print "FAILED PREDICTION!!!!"
					print "FAILED PREDICTION!!!!"
					print "ACTIVE:" + str(len([j for j in my_list if j["breakpoint"].enabled == True]))
					print "FAILED PREDICTION!!!!"
					print "FAILED PREDICTION!!!!"
					


				return False

			mid = (high + low)/2 
			# if the left side is ok 
			# then we know the right must be fucked
			if not will_fail:
				self.enable_jmp_range(mid,high,False)

			left_ok = self.smart_search(low, mid, need_setup=False)
			self.enable_jmp_range(low,mid,False)


			if left_ok: # left side is ok
				print "Left was ok! we know it'll be fucked on the right"
				# make half the right side active
				self.enable_jmp_range(mid,(mid+high)/2,True)
				self.smart_search(mid, high, will_fail=True, need_setup=False)
			else:
				# make the whole right side active
				self.enable_jmp_range(mid,high,True)
				self.smart_search(mid, high, need_setup=False)


			print "Leaving {0}->{1}".format(low, high) 
			return False


			print "This one is fine {0}->{1}".format(low, high) 
			return True