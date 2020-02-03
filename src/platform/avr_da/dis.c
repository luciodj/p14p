/*
 *  Python Bytecode disassember
 */ 

#include <stdio.h>
#include <stdbool.h>
#include <ctype.h>


/* Instruction opcodes for compiled code */

#define STOP_CODE	0
#define POP_TOP		1
#define ROT_TWO		2
#define ROT_THREE	3
#define DUP_TOP		4
#define ROT_FOUR	5

#define NOP		9
#define UNARY_POSITIVE	10
#define UNARY_NEGATIVE	11
#define UNARY_NOT	12
#define UNARY_CONVERT	13

#define UNARY_INVERT	15

#define BINARY_POWER	19

#define BINARY_MULTIPLY	20
#define BINARY_DIVIDE	21
#define BINARY_MODULO	22
#define BINARY_ADD	23
#define BINARY_SUBTRACT	24
#define BINARY_SUBSCR	25
#define BINARY_FLOOR_DIVIDE 26
#define BINARY_TRUE_DIVIDE 27
#define INPLACE_FLOOR_DIVIDE 28
#define INPLACE_TRUE_DIVIDE 29

#define SLICE		30
/* Also uses 31-33 */
#define SLICE_1		31
#define SLICE_2		32
#define SLICE_3		33

#define STORE_SLICE	40
/* Also uses 41-43 */
#define STORE_SLICE_1	41
#define STORE_SLICE_2	42
#define STORE_SLICE_3	43

#define DELETE_SLICE	50
/* Also uses 51-53 */
#define DELETE_SLICE_1	51
#define DELETE_SLICE_2	52
#define DELETE_SLICE_3	53

#define STORE_MAP	54
#define INPLACE_ADD	55
#define INPLACE_SUBTRACT	56
#define INPLACE_MULTIPLY	57
#define INPLACE_DIVIDE	58
#define INPLACE_MODULO	59
#define STORE_SUBSCR	60
#define DELETE_SUBSCR	61

#define BINARY_LSHIFT	62
#define BINARY_RSHIFT	63
#define BINARY_AND	64
#define BINARY_XOR	65
#define BINARY_OR	66
#define INPLACE_POWER	67
#define GET_ITER	68

#define PRINT_EXPR	70
#define PRINT_ITEM	71
#define PRINT_NEWLINE	72
#define PRINT_ITEM_TO   73
#define PRINT_NEWLINE_TO 74
#define INPLACE_LSHIFT	75
#define INPLACE_RSHIFT	76
#define INPLACE_AND	77
#define INPLACE_XOR	78
#define INPLACE_OR	79
#define BREAK_LOOP	80
#define WITH_CLEANUP    81
#define LOAD_LOCALS	82
#define RETURN_VALUE	83
#define IMPORT_STAR	84
#define EXEC_STMT	85
#define YIELD_VALUE	86
#define POP_BLOCK	87
#define END_FINALLY	88
#define BUILD_CLASS	89

#define HAVE_ARGUMENT	90	/* Opcodes from here have an argument: */

#define STORE_NAME	90	/* Index in name list */
#define DELETE_NAME	91	/* "" */
#define UNPACK_SEQUENCE	92	/* Number of sequence items */
#define FOR_ITER	93
#define LIST_APPEND	94

#define STORE_ATTR	95	/* Index in name list */
#define DELETE_ATTR	96	/* "" */
#define STORE_GLOBAL	97	/* "" */
#define DELETE_GLOBAL	98	/* "" */
#define DUP_TOPX	99	/* number of items to duplicate */
#define LOAD_CONST	100	/* Index in const list */
#define LOAD_NAME	101	/* Index in name list */
#define BUILD_TUPLE	102	/* Number of tuple items */
#define BUILD_LIST	103	/* Number of list items */
#define BUILD_SET	104     /* Number of set items */
#define BUILD_MAP	105	/* Always zero for now */
#define LOAD_ATTR	106	/* Index in name list */
#define COMPARE_OP	107	/* Comparison operator */
#define IMPORT_NAME	108	/* Index in name list */
#define IMPORT_FROM	109	/* Index in name list */
#define JUMP_FORWARD	110	/* Number of bytes to skip */

#define JUMP_IF_FALSE_OR_POP 111 /* Target byte offset from beginning
                                    of code */
#define JUMP_IF_TRUE_OR_POP 112	/* "" */
#define JUMP_ABSOLUTE	113	/* "" */
#define POP_JUMP_IF_FALSE 114	/* "" */
#define POP_JUMP_IF_TRUE 115	/* "" */

#define LOAD_GLOBAL	116	/* Index in name list */

#define CONTINUE_LOOP	119	/* Start of loop (absolute) */
#define SETUP_LOOP	120	/* Target address (relative) */
#define SETUP_EXCEPT	121	/* "" */
#define SETUP_FINALLY	122	/* "" */

#define LOAD_FAST	124	/* Local variable number */
#define STORE_FAST	125	/* Local variable number */
#define DELETE_FAST	126	/* Local variable number */

#define RAISE_VARARGS	130	/* Number of raise arguments (1, 2 or 3) */
/* CALL_FUNCTION_XXX opcodes defined below depend on this definition */
#define CALL_FUNCTION	131	/* #args + (#kwargs<<8) */
#define MAKE_FUNCTION	132	/* #defaults */
#define BUILD_SLICE 	133	/* Number of items */

#define MAKE_CLOSURE    134     /* #free vars */
#define LOAD_CLOSURE    135     /* Load free variable from closure */
#define LOAD_DEREF      136     /* Load and dereference from closure cell */ 
#define STORE_DEREF     137     /* Store into cell */ 

/* The next 3 opcodes must be contiguous and satisfy
   (CALL_FUNCTION_VAR - CALL_FUNCTION) & 3 == 1  */
#define CALL_FUNCTION_VAR          140	/* #args + (#kwargs<<8) */
#define CALL_FUNCTION_KW           141	/* #args + (#kwargs<<8) */
#define CALL_FUNCTION_VAR_KW       142	/* #args + (#kwargs<<8) */

#define SETUP_WITH 143

/* Support for opargs more than 16 bits long */
#define EXTENDED_ARG  145

#define SET_ADD         146
#define MAP_ADD         147

char *opcode[] = {
    "STOP_CODE	            ", // 0
    "POP_TOP                ",// 1
    "ROT_TWO                ",// 2
    "ROT_THREE              ", // 3
    "DUP_TOP                ",// 4
    "ROT_FOUR               ",// 5
    "MISSING_6",
    "MISSING_7",
    "MISSING_8",
    "NOP                    ",// 9
    "UNARY_POSITIVE	        ",  // 10
    "UNARY_NEGATIVE	        ",  // 11
    "UNARY_NOT	            ", // 12
    "UNARY_CONVERT	        ", // 13
    "MISSING_14             ",   // 14
    "UNARY_INVERT	        ",// 15
    "MISSING_16             ",   // 16
    "MISSING_17             ",   // 17
    "MISSING_18             ",   // 18
    "BINARY_POWER	        ", // 19
    "BINARY_MULTIPLY	    ",  // 20
    "BINARY_DIVIDE	        ", // 21
    "BINARY_MODULO	        ", // 22
    "BINARY_ADD	            ",  // 23
    "BINARY_SUBTRACT	    ",   // 24
    "BINARY_SUBSCR	        ", // 25
    "BINARY_FLOOR_DIVIDE    ",   // 26
    "BINARY_TRUE_DIVIDE     ",   // 27
    "INPLACE_FLOOR_DIVIDE   ", // 28
    "INPLACE_TRUE_DIVIDE    ", // 29
    "SLICE		            ", // 30
    "SLICE_1                ", // 31
    "SLICE_2                ", // 32
    "SLICE_3                ", // 33
    "MISSING_34             ",   // 34
    "MISSING_35             ",   // 35
    "MISSING_36             ",   // 36
    "MISSING_37             ",   // 37
    "MISSING_38             ",   // 38
    "MISSING_39             ",   // 39
    "STORE_SLICE	        ",   // 40
    "STORE_SLICE_1	        ", // 41
    "STORE_SLICE_2	        ", // 42
    "STORE_SLICE_3	        ", // 43
    "MISSING_44             ",   // 44
    "MISSING_45             ",   // 45
    "MISSING_46             ",   // 46
    "MISSING_47             ",   // 47
    "MISSING_48             ",   // 48
    "MISSING_49             ",   // 49
    "DELETE_SLICE	        ",// 50
    "DELETE_SLICE_1	        ",  // 51
    "DELETE_SLICE_2	        ",  // 52
    "DELETE_SLICE_3	        ",  // 53
    "STORE_MAP	            ", // 54
    "INPLACE_ADD	        ",   // 55
    "INPLACE_SUBTRACT	    ",// 56
    "INPLACE_MULTIPLY	    ",// 57
    "INPLACE_DIVIDE	        ",  // 58
    "INPLACE_MODULO	        ",  // 59
    "STORE_SUBSCR	        ",// 60
    "DELETE_SUBSCR	        ", // 61
    "BINARY_LSHIFT	        ", // 62
    "BINARY_RSHIFT	        ", // 63
    "BINARY_AND	            ",  // 64
    "BINARY_XOR	            ",  // 65
    "BINARY_OR	            ", // 66
    "INPLACE_POWER	        ", // 67
    "GET_ITER	            ",// 68
    "MISSING_69             ",   // 69 ---
    "PRINT_EXPR	            ",  // 70
    "PRINT_ITEM	            ",  // 71
    "PRINT_NEWLINE	        ", // 72
    "PRINT_ITEM_TO          ",   // 73
    "PRINT_NEWLINE_TO       ",   // 74
    "INPLACE_LSHIFT	        ",  // 75
    "INPLACE_RSHIFT	        ",  // 76
    "INPLACE_AND	        ",   // 77
    "INPLACE_XOR	        ",   // 78
    "INPLACE_OR	            ",  // 79
    "BREAK_LOOP	            ",  // 80
    "WITH_CLEANUP           ",   // 81
    "LOAD_LOCALS            ",   // 82
    "RETURN_VALUE           ", // 83
    "IMPORT_STAR            ",   // 84
    "EXEC_STMT              ", // 85
    "YIELD_VALUE            ",   // 86
    "POP_BLOCK              ", // 87
    "END_FINALLY            ",   // 88
    "BUILD_CLASS            ",   // 89
    /* Opcodes from here have an argument: */
    "STORE_NAME	            ",  // 90	/* Index in name list */
    "DELETE_NAME            ",   // 91	/* "" */
    "UNPACK_SEQUENCE	    ",   // 92	/* Number of sequence items */
    "FOR_ITER	            ", // 93
    "LIST_APPEND	        ",   // 94
    "STORE_ATTR	            ",  // 95	/* Index in name list */
    "DELETE_ATTR	        ",   // 96	/* "" */
    "STORE_GLOBAL	        ", // 97	/* "" */
    "DELETE_GLOBAL	        ", // 98	/* "" */
    "DUP_TOPX	            ", // 99	/* number of items to duplicate */
    "LOAD_CONST	            ",  // 100	/* Index in const list */
    "LOAD_NAME	            ", // 101	/* Index in name list */
    "BUILD_TUPLE	        ",   // 102	/* Number of tuple items */
    "BUILD_LIST	            ",  // 103	/* Number of list items */
    "BUILD_SET	            ", // 104     /* Number of set items */
    "BUILD_MAP	            ", // 105	/* Always zero for now */
    "LOAD_ATTR	            ", // 106	/* Index in name list */
    "COMPARE_OP	            ",  // 107	/* Comparison operator */
    "IMPORT_NAME	        ",   // 108	/* Index in name list */
    "IMPORT_FROM	        ",   // 109	/* Index in name list */
    "JUMP_FORWARD	        ",// 110	/* Number of bytes to skip */
    "JUMP_IF_FALSE_OR_POP   ",   // 111 /* Target byte offset from beginning of code */
    "JUMP_IF_TRUE_OR_POP    ",   // 112	/* "" */
    "JUMP_ABSOLUTE	        ", // 113	/* "" */
    "POP_JUMP_IF_FALSE      ",   // 114	/* "" */
    "POP_JUMP_IF_TRUE       ",   // 115	/* "" */
    "LOAD_GLOBAL	        ",   // 116	/* Index in name list */
    "MISSING_117            ",   // 117 
    "MISSING_118            ",   // 118
    "CONTINUE_LOOP	        ", // 119	/* Start of loop (absolute) */
    "SETUP_LOOP	            ",  // 120	/* Target address (relative) */
    "SETUP_EXCEPT	        ",// 121	/* "" */
    "SETUP_FINALLY	        ", // 122	/* "" */
    "MISSING_123            ",   // 123 ---
    "LOAD_FAST	            ", // 124	/* Local variable number */
    "STORE_FAST	            ",  // 125	/* Local variable number */
    "DELETE_FAST	        ",   // 126	/* Local variable number */
    "MISSING_127            ",   // 127 --- 
    "MISSING_128            ",   // 128 --- 
    "MISSING_129            ",   // 129 --- 
    "RAISE_VARARGS	        ", // 130	/* Number of raise arguments (1, 2 or 3) */
     //     /* CALL_FUNCTION_XXX opcodes defined below depend on this definition */
    "CALL_FUNCTION	        ", // 131	/* #args + (#kwargs<<8) */
    "MAKE_FUNCTION	        ", // 132	/* #defaults */
    "BUILD_SLICE 	        ",// 133	/* Number of items */       
    "MAKE_CLOSURE           ",   // 134 /* #free vars */
    "LOAD_CLOSURE           ",   // 135 /* Load free variable from closure */
    "LOAD_DEREF             ",   // 136 /* Load and dereference from closure cell */ 
    "STORE_DEREF            ",   // 137 /* Store into cell */ 
    "MISSING_138            ",   // 138 ---
    "MISSING_139            ",   // 139 ---
    //     /* The next 3 opcodes must be contiguous and satisfy
    //        (CALL_FUNCTION_VAR - CALL_FUNCTION) & 3 == 1  */
    "CALL_FUNCTION_VAR      ",   // 140	/* #args + (#kwargs<<8) */
    "CALL_FUNCTION_KW       ",   // 141	/* #args + (#kwargs<<8) */
    "CALL_FUNCTION_VAR_KW   ",   // 142	/* #args + (#kwargs<<8) */
    "SETUP_WITH             ",   // 143
    "MISSING_144            ",   // 144 ---
    //     /* Support for opargs more than 16 bits long */
    "EXTENDED_ARG           ",   // 145
    "SET_ADD                ",   // 146
    "MAP_ADD                "   // 147
};


char ipm[] = {
    0x0A, 0x1D, 0x01, 0x00, 0x40, 0x02, 0x00, 0x00, // ../lib/ipm.py
    0x11, 0x00, 0x04, 0x04, 0x03, 0x07, 0x00, 0x5F, 
    0x67, 0x65, 0x74, 0x49, 0x6D, 0x67, 0x03, 0x03, 
    0x00, 0x78, 0x30, 0x34, 0x03, 0x03, 0x00, 0x69, 
    0x70, 0x6D, 0x03, 0x03, 0x00, 0x69, 0x70, 0x6D, 
    0x03, 0x04, 0x00, 0x09, 0x39, 0x09, 0x0B, 0x03, 
    0x0E, 0x00, 0x2E, 0x2E, 0x2F, 0x6C, 0x69, 0x62, 
    0x2F, 0x69, 0x70, 0x6D, 0x2E, 0x70, 0x79, 0x00, 
    0x04, 0x04, 0x0B, 0x00, 0x22, 0x00, 0x0B, 0x00, 
    0x23, 0x00, 0x0A, 0xAE, 0x00, 0x01, 0x43, 0x03, 
    0x04, 0x00, 0x55, 0x00, 0x04, 0x07, 0x03, 0x07, 
    0x00, 0x5F, 0x67, 0x65, 0x74, 0x49, 0x6D, 0x67, 
    0x03, 0x02, 0x00, 0x43, 0x6F, 0x03, 0x04, 0x00, 
    0x65, 0x76, 0x61, 0x6C, 0x03, 0x03, 0x00, 0x78, 
    0x30, 0x34, 0x03, 0x05, 0x00, 0x46, 0x61, 0x6C, 
    0x73, 0x65, 0x03, 0x0E, 0x00, 0x41, 0x73, 0x73, 
    0x65, 0x72, 0x74, 0x69, 0x6F, 0x6E, 0x45, 0x72, 
    0x72, 0x6F, 0x72, 0x03, 0x03, 0x00, 0x69, 0x70, 
    0x6D, 0x03, 0x0C, 0x00, 0x00, 0x01, 0x03, 0x04, 
    0x09, 0x01, 0x0C, 0x01, 0x0F, 0x01, 0x0B, 0x04, 
    0x03, 0x0E, 0x00, 0x2E, 0x2E, 0x2F, 0x6C, 0x69, 
    0x62, 0x2F, 0x69, 0x70, 0x6D, 0x2E, 0x70, 0x79, 
    0x00, 0x04, 0x01, 0x00, 0x04, 0x00, 0x78, 0x2F, 
    0x00, 0x74, 0x00, 0x00, 0x83, 0x00, 0x00, 0x7D, 
    0x01, 0x00, 0x74, 0x01, 0x00, 0x7C, 0x01, 0x00, 
    0x83, 0x01, 0x00, 0x7D, 0x02, 0x00, 0x74, 0x02, 
    0x00, 0x7C, 0x02, 0x00, 0x7C, 0x00, 0x00, 0x83, 
    0x02, 0x00, 0x7D, 0x03, 0x00, 0x74, 0x03, 0x00, 
    0x83, 0x00, 0x00, 0x01, 0x71, 0x03, 0x00, 0x57, 
    0x74, 0x04, 0x00, 0x73, 0x3E, 0x00, 0x74, 0x05, 
    0x00, 0x82, 0x01, 0x00, 0x64, 0x00, 0x00, 0x53, 
    0x00, 0x04, 0x00, 0x64, 0x00, 0x00, 0x84, 0x00, 
    0x00, 0x5A, 0x00, 0x00, 0x64, 0x01, 0x00, 0x84, 
    0x00, 0x00, 0x5A, 0x01, 0x00, 0x69, 0x00, 0x00, 
    0x64, 0x02, 0x00, 0x84, 0x01, 0x00, 0x5A, 0x02, 
    0x00, 0x64, 0x03, 0x00, 0x53, 

/* img-list-terminator */
    0xFF, 
};


void list_opcodes(void) {
    for(int i=0; i<148; i++) {
        printf("%d: %s\n", i, opcode[i]);
    }

}

int get_int(char **p) {
    int t16 = (*(*p)++);
    return t16 + (*(*p)++) * 256;
}

int get_byte(char **p) {
    int t8 = (*(*p)++);
    return t8;
}

/* disassemble one instruction */
bool dis(char **pip, char *first) {
    unsigned char op;
    printf("%4ld: ", (*pip)-first);
    op = *(*pip)++;
    if ((int)op > MAP_ADD) 
        printf("Illegal opcode %d!", op);
    else 
        printf("%s", opcode[op]);
    if (op >= HAVE_ARGUMENT) {
        printf("%4d", get_int(pip));
    }
    puts("");
    return (op != STOP_CODE);
}

void ascii_dump(char **p, int size) {
    for(int i=0; i<size; i++) {
        unsigned char c = *(*p)++;
        if (!isprint( c))
            printf("[%02x]", c);
        else
            printf("%c", c);
    }
}

void hex_dump(char **p, int size) {
    for(int i=0; i<size; i++) {
        unsigned char c = *(*p)++;
        printf("%02x, ", c);
    }
}

int unpack_tuple(char **p, int size) {
    int n, r;
    char *first = *p;

    // first element is the type: 
    int type = *(*p)++;
    // printf("Unpacking type %d\n", type);


    switch (type) {
        case 0: // none
            printf("None ");
            break;

        case 1: // integer
            r = get_int(p); 
            printf("Int:%d, ", r);
            break;

        case 10: // code image
            printf("Code image:\n");
            size = get_int(p);
            printf("Size:%d, ", size);
            printf("Argcount:%d, ", get_byte(p));
            printf("Flags:%d, ", get_byte(p));
            printf("Stack:%d, ", get_byte(p));
            printf("Nlocals:%d, ", get_byte(p));
            printf("Freevars:%d, ", get_byte(p));
            printf("First LineNo:%d\n", get_int(p));
            
            printf("Names ");
            r = unpack_tuple(p, size-1);

            printf("Debug info: ");
            printf("Line No Table: ");
            r = unpack_tuple(p, 0);
            printf("\nFilename: ");
            r = unpack_tuple(p, 0);

            printf("\nConst Table: ");
            r = unpack_tuple(p, 0);

            printf("Cell Vars: ");
            r = unpack_tuple(p, 0);

            // hex_dump(p, 10);
            first = *p;
            while ( dis(p, first));
            break;    

        case 3: // string
            // printf("String: ");
            r = get_int(p);
            ascii_dump(p, r);
            size -= r;
            break;

        case 4: // tuple 
            n = get_byte(p);
            printf("[ ");
            while (n-- > 0) {
                printf("%d:", n);
                size -= unpack_tuple(p, size-1);
                printf(", ");
            }
            printf("]\n");
            break;

        case 11: // constant native image
            n = get_byte(p); // argcount
            printf("Native: Argc:%d, ", n);
            r = get_int(p);
            printf("Index:%d ", r);
            size -= 3;
            break;

        default:
            printf("Unknown:%d ", type);
            break;
    }
    return size;
}

int main(int argc, char** argv) {
    char *ip = ipm;
    
    unpack_tuple(&ip, sizeof(ipm));

    // do {
    //     dis(&ip);
    // } while (ip < &ipm[sizeof(ipm)]);
}