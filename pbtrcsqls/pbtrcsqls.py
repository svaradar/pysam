#!/usr/bin/python
#Author: Sam Varadarajan
#Date:   08/14/2012
#Purpose: To extract SQLs from a DBTrace file created by PowerBuilder code.
# This is the python version of the perl script I posted earlier. My attempt to learn Python!
 
import getopt, sys
import codecs
import re
 
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:", ["help", "file="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    fname = None
    for o, a in opts:
        if o in ("-f", "--file"):
            fname = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"
    # ...
 
    if (fname == None):
        usage()
        sys.exit(2)
 
    #flen = 0
    #flen = file_len(fname)
    #print "file length= %d" % (flen, )
    process_file(fname, 'SELECT,INSERT,DELETE,UPDATE')
 
def usage():
    print "\r\nUsage: pbsqls -f <filename>"
    print "\r\n\tWhere filename is the name of the trace log file from PB"
    print "\ttypically saved in Windows directory"
    print "\r\n\tE.g., pbsqls -f c:\\windows\\dbtrace.log > dbtrace.sql"
 
 
def process_file(fname, oplist):
    path = fname
    SQLOP= ()
    SQLOP  = oplist.split(',') # SELECT/INSERT/UPDATE/DELETE
    #print join('|', @SQLOP)
    sql_block_found = 0
    lines = []
    fcount = 0
    line = ''
    result = ''
    print "--" + path + "\r\n"
 
    #PERL:    open LOGFILE, "<:encoding(UCS-2LE)", path or die "Can't open path !\n"
#   LOGFILE = codecs.open(path, encoding="UTF-16-LE")
    str = ''
#        LOGFILE = open(path)
#    while str in iter(LOGFILE):
#        with open(path) as LOGFILE:
    sql_block_found = 0
    with codecs.open(path, encoding="UTF-16-LE") as LOGFILE:
        for str in LOGFILE.readlines():
            str = str.rstrip('\r\n') #PERL chomp
            #print str
 
            if re.search("PREPARE",str):
                    #print str
                    sql_block_found = 1
                    continue
            elif ((sql_block_found == 2) and
            (re.search("GET AFFECTED ROWS:",str) or
            re.search("BIND SELECT OUTPUT BUFFER",str) or
            re.search("DESCRIBE",str) or
            re.search("EXECUTE",str))):
                    #print str
 
                    result = "\r\n".join(lines).upper()
                    # Python equiv. of s// : f=re.sub(searchregx,replacement_str,line)
                    #PERL result =~ s/FROM/\r\nFROM/
                    #result = re.sub(",", ",\r\n", result)
                    result = re.sub(" FROM", "\r\nFROM", result)
                    result = re.sub(" VALUES", "\r\nVALUES", result)
                    result = re.sub(" SET", "\r\nSET", result)
                    result = re.sub(" WHERE", "\r\nWHERE", result)
                    result = re.sub(" AND", "\r\nAND", result)
                    result = re.sub(" ORDER BY", "\r\nORDER BY", result)
                    result = re.sub(" GROUP BY", "\r\nGROUP BY", result)
                    #PERL REDTAG: how?? result =~ s/\([0-9.]+ MS \/ [0-9.]+ MS\)//
                    result = re.sub("(\([0-9.]+ MS \/ [0-9.]+ MS\))", ";\r\n", result)
 
                    #PERL if ($result && $result !~ /FN_SYSDATE/ && $result !~ /NAV_/)
                    if (not re.search("FN_SYSDATE",result) 
                        and not re.search("NAV_", result) 
                        and not re.match("^[ |\t]+;", result)):
                        print result + "\r\n\r\n"
                    sql_block_found = 0
                    lines = []
                    fcount = 0
                    continue
            elif (re.match("^\(.*\):", str)):
                    #PERL $str =~ s/^\(.*\):[ ]*//;
                    str = re.sub("^\(.*\):[ ]*", "", str)
                    #PERL OP: foreach op(@SQLOP):
                    for op in SQLOP:
                        p = re.compile("^"+ op, re.I)
                        if p.match(str):
                            sql_block_found = 2
                            break
 
            if (sql_block_found == 2):
                    #print str + "\n"
                    lines.append(str)
            #PERL elsif (str =~ /\/\*[ ]*[0-9]{2}.*\*\//):
            else:
                p = re.compile("\/\*[ ]*[0-9]{2}.*\*")
                if p.match(str):
                    #remove /* */
                    #PERL $str =~ s/\/\*[ ]*/-- /
                    str = re.sub("\/\*[ ]*", "-- ", str)
                    #PERL $str =~ s/\*\///
                    str = re.sub("\*\/", "", str)
                    #PERL push(@lines, $str)
                    lines.append(str)
    LOGFILE.close()
 
 
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    f.close
    return i + 1
 
 
if __name__ == "__main__":
    main()
