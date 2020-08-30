#!/usr/bin/python
"""Author: Sam Varadarajan
Date:   08/14/2012
Purpose: To extract SQLs from a DBTrace file created by PowerBuilder code.
This is the python version of the perl script I posted earlier. My attempt to learn Python!
"""

import getopt
import sys
import codecs
import re

def process_file(fname, sqlops):
    """ Process the Trace file to extract SQLs"""
    path = fname
    #sqlops= ()
    #sqlops  = oplist.split(',') # SELECT/INSERT/UPDATE/DELETE
    #print(sqlops,)
    sql_block_found = 0
    lines = []
    #fcount = 0
    line = ''
    result = ''
    print("--" + path + "\r\n")

    #PERL:    open logfp, "<:encoding(UCS-2LE)", path or die "Can't open path !\n"
#   logfp = codecs.open(path, encoding="UTF-16-LE")
    line = ''
#        logfp = open(path)
#    while line in iter(logfp):
#        with open(path) as logfp:
    sql_block_found = 0
    with codecs.open(path) as logfp:
        for line in logfp.readlines():
            line = line.rstrip('\r\n') #PERL chomp
            #debug print(line)

            if re.search("PREPARE",line):
                #debug print(line)
                sql_block_found = 1
                #continue
            elif ((sql_block_found == 2) and
            (re.search("GET AFFECTED ROWS:",line) or
            re.search("BIND SELECT OUTPUT BUFFER",line) or
            re.search("DESCRIBE",line) or
            re.search("EXECUTE",line))):
                #print line

                result = "\r\n".join(lines).upper()
                # Python equiv. of s// : infile=re.sub(searchregx,replacement_str,line)
                #PERL result =~ s/FROM/\r\nFROM/
                #result = re.sub(",", ",\r\n", result)
                result = re.sub(r" FROM", "\r\nFROM", result)
                result = re.sub(r" VALUES", "\r\nVALUES", result)
                result = re.sub(r" SET", "\r\nSET", result)
                result = re.sub(r" WHERE", "\r\nWHERE", result)
                result = re.sub(r" AND", "\r\nAND", result)
                result = re.sub(r" ORDER BY", "\r\nORDER BY", result)
                result = re.sub(r" GROUP BY", "\r\nGROUP BY", result)
                #PERL REDTAG: how?? result =~ s/\([0-9.]+ MS \/ [0-9.]+ MS\)//
                result = re.sub(r"(\([0-9.]+ MS \/ [0-9.]+ MS\))", ";\r\n", result)

                #PERL if ($result && $result !~ /FN_SYSDATE/ && $result !~ /NAV_/)
                if (not re.search("FN_SYSDATE",result)
                    and not re.search("NAV_", result)
                    and not re.match("^[ |\t]+;", result)):
                    print(result + "\r\n\r\n")
                sql_block_found = 0
                lines = []
                #fcount = 0
                continue
            elif re.match(r"^\(.*\):", line):
                #PERL $line =~ s/^\(.*\):[ ]*//;
                line = re.sub(r"^\(.*\):[ ]*", "", line)
                #PERL sqlop: foreach sqlop(@3):
                for sqlop in sqlops:
                    #print(sqlop)
                    pattern = re.compile(r"^"+ sqlop, re.I)
                    if pattern.match(line):
                        sql_block_found = 2
                        break

            if sql_block_found == 2:
                print(line + "\n")
                lines.append(line)
            #PERL elsif (line =~ /\/\*[ ]*[0-9]{2}.*\*\//):
            else:
                pattern = re.compile(r"\/\*[ ]*[0-9]{2}.*\*")
                if pattern.match(line):
                    #remove /* */
                    #PERL $line =~ s/\/\*[ ]*/-- /
                    line = re.sub(r"\/\*[ ]*", "-- ", line)
                    #PERL $line =~ s/\*\///
                    line = re.sub(r"\*\/", "", line)
                    #PERL push(@lines, $line)
                    lines.append(line)
    logfp.close()


# def file_len(fname):
    # with open(fname) as infile:
        # for cnt, line in enumerate(infile):
            # pass
    # #infile.close
    # return  cnt + 1

def usage():
    """
    Usage: pbsqls -f <filename>
        Where filename is the name of the trace log file from PB
        typically saved in Windows directory
        E.g., pbsqls -f c:\\windows\\dbtrace.log > dbtrace.sql
    """
    return None


def main():
    """ this is the main function"""
    try:
        opts, _args = getopt.getopt(sys.argv[1:], "hf:", ["help", "file="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        print(usage.__doc__)
        sys.exit(2)

    fname = None
    for key, value in opts:
        if key in ("-f", "--file"):
            fname = value
        elif key in ("-h", "--help"):
            print(usage.__doc__)
            sys.exit()
        else:
            assert False, "unhandled option"
    # ...

    if fname is None:
        print(usage.__doc__)
        sys.exit(2)

    ops = ("SELECT", "INSERT", "DELETE", "UPDATE")
    #flen = 0
    #flen = file_len(fname)
    #print("file length= %d" % (flen, ))
    process_file(fname,ops)


if __name__ == "__main__":
    main()
