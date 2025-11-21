#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symbol_table.h"

SymbolTable* symbol_table_new() {
    SymbolTable* table = malloc(sizeof(SymbolTable));
    table->count = 0;
    table->static_count = 0;
    table->field_count = 0;
    table->arg_count = 0;
    table->var_count = 0;
    return table;
}

void symbol_table_free(SymbolTable* table) {
    if (!table) return;
    
    for (int i = 0; i < table->count; i++) {
        free(table->symbols[i].name);
        free(table->symbols[i].type);
    }
    free(table);
}

void symbol_table_start_subroutine(SymbolTable* table) {
    if (!table) return;
    
    /* Clear subroutine-scoped symbols (ARG and VAR) */
    int new_count = 0;
    for (int i = 0; i < table->count; i++) {
        if (table->symbols[i].kind == KIND_STATIC || table->symbols[i].kind == KIND_FIELD) {
            if (new_count != i) {
                table->symbols[new_count] = table->symbols[i];
            }
            new_count++;
        } else {
            /* Free subroutine-scoped symbols */
            free(table->symbols[i].name);
            free(table->symbols[i].type);
        }
    }
    
    table->count = new_count;
    table->arg_count = 0;
    table->var_count = 0;
}

void symbol_table_define(SymbolTable* table, const char* name, const char* type, Kind kind) {
    if (!table || table->count >= MAX_SYMBOLS) return;
    
    Symbol* symbol = &table->symbols[table->count];
    symbol->name = strdup(name);
    symbol->type = strdup(type);
    symbol->kind = kind;
    
    switch (kind) {
        case KIND_STATIC:
            symbol->index = table->static_count++;
            break;
        case KIND_FIELD:
            symbol->index = table->field_count++;
            break;
        case KIND_ARG:
            symbol->index = table->arg_count++;
            break;
        case KIND_VAR:
            symbol->index = table->var_count++;
            break;
        default:
            symbol->index = 0;
    }
    
    table->count++;
}

int symbol_table_var_count(SymbolTable* table, Kind kind) {
    if (!table) return 0;
    
    switch (kind) {
        case KIND_STATIC: return table->static_count;
        case KIND_FIELD: return table->field_count;
        case KIND_ARG: return table->arg_count;
        case KIND_VAR: return table->var_count;
        default: return 0;
    }
}

Kind symbol_table_kind_of(SymbolTable* table, const char* name) {
    if (!table || !name) return KIND_NONE;
    
    for (int i = 0; i < table->count; i++) {
        if (strcmp(table->symbols[i].name, name) == 0) {
            return table->symbols[i].kind;
        }
    }
    
    return KIND_NONE;
}

char* symbol_table_type_of(SymbolTable* table, const char* name) {
    if (!table || !name) return NULL;
    
    for (int i = 0; i < table->count; i++) {
        if (strcmp(table->symbols[i].name, name) == 0) {
            return table->symbols[i].type;
        }
    }
    
    return NULL;
}

int symbol_table_index_of(SymbolTable* table, const char* name) {
    if (!table || !name) return -1;
    
    for (int i = 0; i < table->count; i++) {
        if (strcmp(table->symbols[i].name, name) == 0) {
            return table->symbols[i].index;
        }
    }
    
    return -1;
}