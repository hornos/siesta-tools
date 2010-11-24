#!/usr/bin/env python

import sys, string
from xml.sax import handler, make_parser, saxutils


### Functions
def normalize_whitespace( text ):
    return string.strip( text )


# class orbital
class orbital:
    def __init__( self ):
	self.orbital_index = 0
	self.atom_index = 0
	self.species  = 'X'
	self.position = [0.000, 0.000, 0.000]
	self.nlmz = [0, 0, 0, 0]
	self.dos = [[],[]]
# end class orbital


# class pdosData
class pdosData:
    def __init__( self ):
	self.nspin = 0
	self.norbitals = 0
	self.natoms = 0
	self.energy_values = []
	self.orbitals = []
# end class pdosData


# class pdosHandler
class pdosHandler( handler.ContentHandler ):
    def __init__( self, data ):
	self.data   = data
	self.parts  = { 'nspin': 0, 'norbitals': 0, 'energy_values': 0, 'orbital': 0, 'data': 0 }
	self.line   = ""
	self.orbidx = 0
	self.atmidx = 0
    #

    def startDocument( self ):
	print "Reading started"

    def endDocument( self ):
	# print "Reading finished"
	self.data.natoms = self.atmidx

    def startElement( self, name, attrs ):
	for key, val in self.parts.iteritems():
	    if( name == key ):
		self.parts[key] = 1;

	if( self.parts['orbital'] ):
	    orb = orbital()
	    ok = 1

	    val = attrs.get( 'index' )
	    if( val != None ):
		val = string.atoi( normalize_whitespace( attrs.get( 'index' ) ) )
		self.orbidx = (val - 1)
		orb.orbital_index = val
	    else:
		ok = 0
		
	    val = attrs.get( 'atom_index' )
	    if( val != None ):
		val = string.atoi( normalize_whitespace( attrs.get( 'atom_index' ) ) )
		self.atmidx = val
		orb.atom_index = val
	    else:
		ok = 0

	    val = attrs.get( 'species' )
	    if( val != None ):
		val = str( normalize_whitespace( attrs.get( 'species' ) ) )
		orb.species = val
	    else:
		ok = 0

	    val = attrs.get( 'position' )
	    if( val != None ):
		lin = normalize_whitespace( attrs.get( 'position' ) )
		pos = lin.split()
		orb.position[0] = string.atof( pos[0] )
		orb.position[1] = string.atof( pos[1] )
		orb.position[2] = string.atof( pos[2] )
	    else:
		ok = 0
		
	    val = attrs.get( 'n' )
	    if( val != None ):
		val = string.atoi( normalize_whitespace( attrs.get( 'n' ) ) )
		orb.nlmz[0] = val
	    else:
		ok = 0

	    val = attrs.get( 'l' )
	    if( val != None ):
		val = string.atoi( normalize_whitespace( attrs.get( 'l' ) ) )
		orb.nlmz[1] = val
	    else:
		ok = 0
	    
	    val = attrs.get( 'm' )
	    if( val != None ):
		val = normalize_whitespace( attrs.get( 'm' ) )
		if( val != '*' ):
		    val = string.atoi( val )

		orb.nlmz[2] = val
	    else:
		ok = 0

	    val = attrs.get( 'z' )
	    if( val != None ):
		val = string.atoi( normalize_whitespace( attrs.get( 'z' ) ) )
		orb.nlmz[3] = val
	    else:
		ok = 0
		
	    if( ok ):
    		self.data.orbitals.append( orb )
	# end orbital part	
    # end startElement


    def endElement( self, name ):
	for key, val in self.parts.iteritems():
	    if( name == key ):
		self.parts[key] = 0;
    #

    def characters( self, ch ):
	if( self.parts['nspin'] ):
	    self.data.nspin = string.atoi( normalize_whitespace( ch ) )

	if( self.parts['norbitals'] ):
	    self.data.norbitals = string.atoi( normalize_whitespace( ch ) )
	    
	if( self.parts['energy_values'] ):
	    if( ch != '\n' ):
		self.data.energy_values.append( string.atof( normalize_whitespace( ch ) ) )
	
	if( self.parts['orbital'] and self.parts['data'] ):
	    if( ch != '\n' ):
		self.line += ch
	    else:
		lin = normalize_whitespace( self.line )
		if( self.line != "" ):
		    dos = lin.split();
		    alpha = string.atof( dos[0] )
		    self.data.orbitals[self.orbidx].dos[0].append( alpha )
		    
		    if( self.data.nspin == 2 ):
			beta  = string.atof( dos[1] )
			self.data.orbitals[self.orbidx].dos[1].append( beta )
		    #
		    self.line = ""
		#
	    #
	#
    #
# end class pdosHandler

def getqn( nlmz ):
    return nlmz[0]

def getql( nlmz ):
    ql = [ 's', 'p', 'd', 'f' ]
    return ql[nlmz[1]]

def getqm( nlmz ):
    if( nlmz[2] == 0 ):
	return 'z'

    if( nlmz[2] == 1 ):
	return 'x'

    if( nlmz[2] == -1 ):
	return 'y'
	
    return str( nlmz[2] )



def pdoswrite( idx, data ):
    orbitals = []
    
    # print data.orbitals[2569].dos[0]
    
    i = 0
    for orb in data.orbitals:
	if( orb.atom_index == idx ):
	    orbitals.append( i )
	i += 1

    print "Found in: "+str(orbitals)

    for s in range(data.nspin):
	total = []
	output = "pdos_s_"+str(s)+"_a_"+str(idx)+".dat"
	fp = open( output, "w")
    
	fp.write( "%14s" % "Energy[eV]" )
    
    
	for i in orbitals:
	    fp.write( "\t%s%d%s%s%d" % ("nlmz=", getqn( data.orbitals[i].nlmz ), getql( data.orbitals[i].nlmz ), getqm( data.orbitals[i].nlmz ), data.orbitals[i].nlmz[3]) )
    
	fp.write( "\t%s" % "Total" )    
	fp.write( "\n" )
    
	j = 0
	for eng in data.energy_values:
	    total.append( 0.000 )
	    
	    fp.write( "%12.5f" % eng )
	
	    for i in orbitals:
		#print data.orbitals[i].dos[0][0]
		fp.write( "\t%9.5f" % data.orbitals[i].dos[s][j] )
		total[j] += data.orbitals[i].dos[s][j]
		# print orb.dos[0]
	    # end for i
	    fp.write( "\t%9.5f" % total[j] )
	    fp.write( "\n" );
	    j += 1
	# end for eng
	fp.close()
    # end for s
    
def pdosreader( inp, data ):

    handler = pdosHandler( data )
    parser = make_parser()

    parser.setContentHandler( handler )
    inFile = open( inp, 'r' )

    parser.parse( inFile )

    inFile.close()
#



def main():
    data    = pdosData()

    args = sys.argv[1:]
    
    if len( args ) < 2:
        print "usage: "+sys.argv[0]+" input atomno"
        sys.exit( -1 )

    pdosreader( args[0], data )
    pdoswrite( string.atoi( args[1] ), data )


if __name__ == '__main__':
    main()
