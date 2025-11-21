%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symbol_table.h"
#include "vm_writer.h"

extern int yylex();
extern int yylineno;
extern FILE* yyin;

void yyerror(const char* s);

/* Global variables */
SymbolTable* class_table;
SymbolTable* subroutine_table;
VMWriter* vm_writer;
char* current_class_name;
char* current_subroutine_name;
char* current_subroutine_type; /* function, method, constructor */
int label_counter = 0;

/* Context for variable declarations */
char* current_var_type = NULL;
Kind current_var_kind = KIND_NONE;

/* Label stack for control structures */
#define MAX_LABEL_STACK 100
char* label_stack[MAX_LABEL_STACK];
int label_stack_top = -1;

void push_labels(char* label1, char* label2) {
    if (label_stack_top < MAX_LABEL_STACK - 2) {
        label_stack[++label_stack_top] = label1;
        if (label2) label_stack[++label_stack_top] = label2;
    }
}

char* pop_label() {
    return (label_stack_top >= 0) ? label_stack[label_stack_top--] : NULL;
}

/* Helper functions */
char* generate_label(const char* prefix);
void compile_subroutine_call(const char* class_name, const char* subroutine_name, int arg_count);
void compile_var_access(const char* var_name, int is_assignment);
%}

%union {
    int integer;
    char* string;
}

/* Token declarations */
%token CLASS CONSTRUCTOR FUNCTION METHOD FIELD STATIC VAR
%token INT CHAR BOOLEAN VOID TRUE FALSE NULL_TOKEN THIS
%token LET DO IF ELSE WHILE RETURN
%token LBRACE RBRACE LPAREN RPAREN LBRACKET RBRACKET
%token DOT COMMA SEMICOLON
%token PLUS MINUS MULTIPLY DIVIDE AND OR LT GT EQ NOT
%token <string> IDENTIFIER STRING_CONSTANT
%token <integer> INTEGER_CONSTANT

/* Non-terminal types */
%type <string> type return_type
%type <integer> expression term subroutine_call expression_list expression_list_non_empty field_or_static

/* Operator precedence (lowest to highest) */
%left OR
%left AND
%left EQ LT GT
%left PLUS MINUS
%left MULTIPLY DIVIDE
%right NOT
%right UMINUS


%%

/* Grammar Rules with Actions */

class: CLASS IDENTIFIER {
    current_class_name = strdup($2);
    printf("Compiling class: %s\n", current_class_name);
} LBRACE class_var_dec_list subroutine_dec_list RBRACE
;

class_var_dec_list: /* empty */
| class_var_dec_list class_var_dec
;

class_var_dec: field_or_static {
    current_var_kind = $1;
} type {
    current_var_type = strdup($3);
} var_list SEMICOLON
;

field_or_static: FIELD { $$ = KIND_FIELD; }
| STATIC { $$ = KIND_STATIC; }
;

type: INT { $$ = strdup("int"); }
| CHAR { $$ = strdup("char"); }
| BOOLEAN { $$ = strdup("boolean"); }
| IDENTIFIER { $$ = $1; }
;

var_list: var_list COMMA IDENTIFIER {
    if (current_var_kind == KIND_FIELD || current_var_kind == KIND_STATIC) {
        symbol_table_define(class_table, $3, current_var_type, current_var_kind);
    } else {
        symbol_table_define(subroutine_table, $3, current_var_type, current_var_kind);
    }
}
| IDENTIFIER {
    if (current_var_kind == KIND_FIELD || current_var_kind == KIND_STATIC) {
        symbol_table_define(class_table, $1, current_var_type, current_var_kind);
    } else {
        symbol_table_define(subroutine_table, $1, current_var_type, current_var_kind);
    }
}
;

subroutine_dec_list: /* empty */
| subroutine_dec_list subroutine_dec
;

subroutine_dec: subroutine_type return_type IDENTIFIER {
    current_subroutine_name = strdup($3);
    symbol_table_start_subroutine(subroutine_table);

    /* For methods, add 'this' as argument 0 */
    if (strcmp(current_subroutine_type, "method") == 0) {
        symbol_table_define(subroutine_table, "this", current_class_name, KIND_ARG);
    }

    printf("Compiling subroutine: %s.%s\n", current_class_name, current_subroutine_name);
} LPAREN parameter_list RPAREN subroutine_body
;

subroutine_type: CONSTRUCTOR { current_subroutine_type = strdup("constructor"); }
| FUNCTION { current_subroutine_type = strdup("function"); }
| METHOD { current_subroutine_type = strdup("method"); }
;

return_type: type { $$ = $1; }
| VOID { $$ = strdup("void"); }
;

parameter_list: /* empty */
| parameter_list_non_empty
;

parameter_list_non_empty: type IDENTIFIER {
    /* Add parameter to symbol table */
    symbol_table_define(subroutine_table, $2, $1, KIND_ARG);
}
| parameter_list_non_empty COMMA type IDENTIFIER {
    symbol_table_define(subroutine_table, $4, $3, KIND_ARG);
}
;

subroutine_body: LBRACE var_dec_list {
    /* Generate VM function after processing local variables */
    char function_name[256];
    snprintf(function_name, sizeof(function_name), "%s.%s", current_class_name, current_subroutine_name);

    int local_count = symbol_table_var_count(subroutine_table, KIND_VAR);
    vm_writer_write_function(vm_writer, function_name, local_count);

    /* Handle method initialization */
    if (strcmp(current_subroutine_type, "method") == 0) {
        vm_writer_write_push(vm_writer, SEG_ARG, 0);
        vm_writer_write_pop(vm_writer, SEG_POINTER, 0);
    } else if (strcmp(current_subroutine_type, "constructor") == 0) {
        int field_count = symbol_table_var_count(class_table, KIND_FIELD);
        vm_writer_write_push(vm_writer, SEG_CONST, field_count);
        vm_writer_write_call(vm_writer, "Memory.alloc", 1);
        vm_writer_write_pop(vm_writer, SEG_POINTER, 0);
    }
} statements RBRACE
;

var_dec_list: /* empty */
| var_dec_list var_dec
;

var_dec: VAR {
    current_var_kind = KIND_VAR;
} type {
    current_var_type = strdup($3);
} var_list SEMICOLON
;

statements: /* empty */
| statements statement
;

statement: let_statement
| if_statement
| while_statement
| do_statement
| return_statement
;

let_statement: LET IDENTIFIER EQ expression SEMICOLON {
    /* Simple variable assignment */
    compile_var_access($2, 1);
}
| LET IDENTIFIER LBRACKET expression RBRACKET EQ expression SEMICOLON {
    /* Array assignment: arr[i] = expr */
    /* Push array base */
    compile_var_access($2, 0);
    /* expression for index already on stack */
    vm_writer_write_arithmetic(vm_writer, CMD_ADD);
    /* Store array address in temp */
    vm_writer_write_pop(vm_writer, SEG_TEMP, 0);
    /* Pop value to assign */
    vm_writer_write_pop(vm_writer, SEG_TEMP, 1);
    /* Set that pointer to array address */
    vm_writer_write_push(vm_writer, SEG_TEMP, 0);
    vm_writer_write_pop(vm_writer, SEG_POINTER, 1);
    /* Store value */
    vm_writer_write_push(vm_writer, SEG_TEMP, 1);
    vm_writer_write_pop(vm_writer, SEG_THAT, 0);
}
;

if_statement: IF LPAREN expression RPAREN LBRACE statements RBRACE {
    /* Simple if statement - generate code after parsing */
    char* end_label = generate_label("IF_END");
    vm_writer_write_arithmetic(vm_writer, CMD_NOT);
    vm_writer_write_if(vm_writer, end_label);
    vm_writer_write_label(vm_writer, end_label);
}
| IF LPAREN expression RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE {
    /* If-else statement - generate code after parsing */
    char* else_label = generate_label("IF_ELSE");
    char* end_label = generate_label("IF_END");
    vm_writer_write_arithmetic(vm_writer, CMD_NOT);
    vm_writer_write_if(vm_writer, else_label);
    vm_writer_write_goto(vm_writer, end_label);
    vm_writer_write_label(vm_writer, else_label);
    vm_writer_write_label(vm_writer, end_label);
}
;

while_statement: WHILE {
    char* start_label = generate_label("WHILE_START");
    char* end_label = generate_label("WHILE_END");
    push_labels(start_label, end_label);
    vm_writer_write_label(vm_writer, start_label);
} LPAREN expression RPAREN {
    char* end_label = label_stack[label_stack_top];
    vm_writer_write_arithmetic(vm_writer, CMD_NOT);
    vm_writer_write_if(vm_writer, end_label);
} LBRACE statements RBRACE {
    char* end_label = pop_label();
    char* start_label = pop_label();
    vm_writer_write_goto(vm_writer, start_label);
    vm_writer_write_label(vm_writer, end_label);
}
;

do_statement: DO subroutine_call SEMICOLON {
    /* Discard return value from void subroutine */
    vm_writer_write_pop(vm_writer, SEG_TEMP, 0);
}
;

return_statement: RETURN SEMICOLON {
    /* Return from void function */
    vm_writer_write_push(vm_writer, SEG_CONST, 0);
    vm_writer_write_return(vm_writer);
}
| RETURN expression SEMICOLON {
    /* Return with value - expression result already on stack */
    vm_writer_write_return(vm_writer);
}
;

expression: term { $$ = $1; }
| expression PLUS expression {
    vm_writer_write_arithmetic(vm_writer, CMD_ADD);
    $$ = 1;
}
| expression MINUS expression {
    vm_writer_write_arithmetic(vm_writer, CMD_SUB);
    $$ = 1;
}
| expression MULTIPLY expression {
    vm_writer_write_call(vm_writer, "Math.multiply", 2);
    $$ = 1;
}
| expression DIVIDE expression {
    vm_writer_write_call(vm_writer, "Math.divide", 2);
    $$ = 1;
}
| expression AND expression {
    vm_writer_write_arithmetic(vm_writer, CMD_AND);
    $$ = 1;
}
| expression OR expression {
    vm_writer_write_arithmetic(vm_writer, CMD_OR);
    $$ = 1;
}
| expression LT expression {
    vm_writer_write_arithmetic(vm_writer, CMD_LT);
    $$ = 1;
}
| expression GT expression {
    vm_writer_write_arithmetic(vm_writer, CMD_GT);
    $$ = 1;
}
| expression EQ expression {
    vm_writer_write_arithmetic(vm_writer, CMD_EQ);
    $$ = 1;
}
| MINUS expression %prec UMINUS {
    vm_writer_write_arithmetic(vm_writer, CMD_NEG);
    $$ = 1;
}
| NOT expression {
    vm_writer_write_arithmetic(vm_writer, CMD_NOT);
    $$ = 1;
}
;

term: INTEGER_CONSTANT {
    vm_writer_write_push(vm_writer, SEG_CONST, $1);
    $$ = 1;
}
| STRING_CONSTANT {
    /* Create string constant */
    int len = strlen($1);
    vm_writer_write_push(vm_writer, SEG_CONST, len);
    vm_writer_write_call(vm_writer, "String.new", 1);

    for (int i = 0; i < len; i++) {
        vm_writer_write_push(vm_writer, SEG_CONST, (int)$1[i]);
        vm_writer_write_call(vm_writer, "String.appendChar", 2);
    }
    $$ = 1;
}
| TRUE {
    vm_writer_write_push(vm_writer, SEG_CONST, 1);
    vm_writer_write_arithmetic(vm_writer, CMD_NEG);
    $$ = 1;
}
| FALSE {
    vm_writer_write_push(vm_writer, SEG_CONST, 0);
    $$ = 1;
}
| NULL_TOKEN {
    vm_writer_write_push(vm_writer, SEG_CONST, 0);
    $$ = 1;
}
| THIS {
    vm_writer_write_push(vm_writer, SEG_POINTER, 0);
    $$ = 1;
}
| IDENTIFIER {
    compile_var_access($1, 0);
    $$ = 1;
}
| IDENTIFIER LBRACKET expression RBRACKET {
    /* Array access: arr[i] */
    compile_var_access($1, 0);
    vm_writer_write_arithmetic(vm_writer, CMD_ADD);
    vm_writer_write_pop(vm_writer, SEG_POINTER, 1);
    vm_writer_write_push(vm_writer, SEG_THAT, 0);
    $$ = 1;
}
| subroutine_call {
    $$ = 1;
}
| LPAREN expression RPAREN {
    $$ = $2;
}
;

subroutine_call: IDENTIFIER LPAREN expression_list RPAREN {
    /* Method call on current object or function call */
    char function_name[256];

    /* Check if it's a method call (need to push 'this') */
    if (strcmp(current_subroutine_type, "method") == 0 ||
        symbol_table_kind_of(subroutine_table, $1) == KIND_NONE &&
        symbol_table_kind_of(class_table, $1) == KIND_NONE) {
        /* Assume it's a method on current object */
        snprintf(function_name, sizeof(function_name), "%s.%s", current_class_name, $1);
        vm_writer_write_push(vm_writer, SEG_POINTER, 0); /* Push this */
        vm_writer_write_call(vm_writer, function_name, $3 + 1);
    } else {
        /* It's a function call */
        snprintf(function_name, sizeof(function_name), "%s.%s", current_class_name, $1);
        vm_writer_write_call(vm_writer, function_name, $3);
    }
    $$ = 1;
}
| IDENTIFIER DOT IDENTIFIER LPAREN expression_list RPAREN {
    /* Method/function call on other object or class */
    Kind kind = symbol_table_kind_of(subroutine_table, $1);
    if (kind == KIND_NONE) {
        kind = symbol_table_kind_of(class_table, $1);
    }

    char function_name[256];
    if (kind != KIND_NONE) {
        /* Method call on object variable */
        compile_var_access($1, 0);
        char* type = symbol_table_type_of(subroutine_table, $1);
        if (!type) {
            type = symbol_table_type_of(class_table, $1);
        }
        snprintf(function_name, sizeof(function_name), "%s.%s", type, $3);
        vm_writer_write_call(vm_writer, function_name, $5 + 1);
    } else {
        /* Function call or constructor */
        snprintf(function_name, sizeof(function_name), "%s.%s", $1, $3);
        vm_writer_write_call(vm_writer, function_name, $5);
    }
    $$ = 1;
}
;

expression_list: /* empty */ {
    $$ = 0;
}
| expression_list_non_empty {
    $$ = $1;
}
;

expression_list_non_empty: expression {
    $$ = 1;
}
| expression_list_non_empty COMMA expression {
    $$ = $1 + 1;
}
;

%%

void yyerror(const char* s) {
    fprintf(stderr, "Error at line %d: %s\n", yylineno, s);
}

char* generate_label(const char* prefix) {
    char* label = malloc(64);
    snprintf(label, 64, "%s_%d", prefix, label_counter++);
    return label;
}

void compile_var_access(const char* var_name, int is_assignment) {
    Kind kind = symbol_table_kind_of(subroutine_table, var_name);
    SymbolTable* table = subroutine_table;
    if (kind == KIND_NONE) {
        kind = symbol_table_kind_of(class_table, var_name);
        table = class_table;
    }

    Segment seg;
    int index;
    if (kind == KIND_VAR) {
        seg = SEG_LOCAL;
        index = symbol_table_index_of(table, var_name);
    } else if (kind == KIND_ARG) {
        seg = SEG_ARG;
        index = symbol_table_index_of(table, var_name);
    } else if (kind == KIND_FIELD) {
        seg = SEG_THIS;
        index = symbol_table_index_of(table, var_name);
    } else if (kind == KIND_STATIC) {
        seg = SEG_STATIC;
        index = symbol_table_index_of(table, var_name);
    } else {
        /* Unknown variable - use temp segment as fallback */
        fprintf(stderr, "Warning: Unknown variable %s\n", var_name);
        seg = SEG_TEMP;
        index = 0;
    }

    if (!is_assignment) {
        vm_writer_write_push(vm_writer, seg, index);
    } else {
        vm_writer_write_pop(vm_writer, seg, index);
    }
}

int main(int argc, char** argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <input.jack>\n", argv[0]);
        return 1;
    }

    /* Open input file */
    yyin = fopen(argv[1], "r");
    if (!yyin) {
        perror("Error opening input file");
        return 1;
    }

    /* Create output file name */
    char* output_name = strdup(argv[1]);
    char* dot = strrchr(output_name, '.');
    if (dot) *dot = '\0';
    strcat(output_name, ".vm");

    /* Initialize global structures */
    class_table = symbol_table_new();
    subroutine_table = symbol_table_new();
    vm_writer = vm_writer_new(output_name);

    if (!vm_writer) {
        fprintf(stderr, "Error creating output file: %s\n", output_name);
        return 1;
    }

    printf("Compiling %s to %s\n", argv[1], output_name);

    /* Parse the input */
    int result = yyparse();

    if (result == 0) {
        printf("Compilation successful!\n");
    } else {
        printf("Compilation failed!\n");
    }

    /* Cleanup */
    fclose(yyin);
    symbol_table_free(class_table);
    symbol_table_free(subroutine_table);
    vm_writer_close(vm_writer);
    free(output_name);

    return result;
}
