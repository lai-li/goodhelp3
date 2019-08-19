import twder
def currencySearch(search):
	dollarTuple = twder.now(search)
	#dollarTuple = twder.now_all()[search]
	reply = '{}\n{},{}'.format(dollarTuple[0],search, dollarTuple[4])
	return reply