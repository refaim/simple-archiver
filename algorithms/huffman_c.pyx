# -*- coding: utf-8 -*-

#cpdef list uncompress(chunk, dict code_table):
#    result = []
#    cdef unsigned int length = 0, i = 0
#    cdef unsigned int code = 0
#    for byte in chunk:
#        for i from 0 <= i < 8:
#            if byte & (1 << i) != 0:
#                code ^= 1 << length
#            length += 1
#            if (code, length) in code_table:
#                result.append(code_table[(code, length)])
#                code = 0
#                length = 0
#    return result

cpdef list uncompress(chunk, dict code_table):
    result = []
    
    for k, v in sorted(code_table.iteritems()):
        print k, ord(v)
    #exit()

    cdef unsigned char length = 0, i = 0
    cdef unsigned long code = 0
    for byte in chunk:
        #if length >= 8:
        #    code <<= 8
        for i from 0 <= i < 8:
            if byte & (1 << i):
                code ^= 1 << length
            length += 1
            print (code, length), bin(code), hex(code)
            if (code, length) in code_table:
                result.append(code_table[(code, length)])
                code = 0
                length = 0
    return result
