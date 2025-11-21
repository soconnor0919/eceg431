#ifndef SYMBOL_TABLE_H
#define SYMBOL_TABLE_H

#define MAX_SYMBOLS 1000

/* Symbol kinds */
typedef enum {
    KIND_STATIC,
    KIND_FIELD, 
    KIND_ARG,
    KIND_VAR,
    KIND_NONE
} Kind;

/* Symbol table entry */
typedef struct {
    char* name;
    char* type;
    Kind kind;
    int index;
} Symbol;

/* Symbol table structure */
typedef struct {
    Symbol symbols[MAX_SYMBOLS];
    int count;
    int static_count;
    int field_count;
    int arg_count;
    int var_count;
} SymbolTable;

/* Function prototypes */
SymbolTable* symbol_table_new();
void symbol_table_free(SymbolTable* table);
void symbol_table_start_subroutine(SymbolTable* table);
void symbol_table_define(SymbolTable* table, const char* name, const char* type, Kind kind);
int symbol_table_var_count(SymbolTable* table, Kind kind);
Kind symbol_table_kind_of(SymbolTable* table, const char* name);
char* symbol_table_type_of(SymbolTable* table, const char* name);
int symbol_table_index_of(SymbolTable* table, const char* name);

#endif