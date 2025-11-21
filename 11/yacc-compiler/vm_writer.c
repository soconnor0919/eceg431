#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "vm_writer.h"

VMWriter* vm_writer_new(const char* filename) {
    VMWriter* writer = malloc(sizeof(VMWriter));
    writer->file = fopen(filename, "w");
    if (!writer->file) {
        free(writer);
        return NULL;
    }
    return writer;
}

void vm_writer_close(VMWriter* writer) {
    if (!writer) return;
    
    if (writer->file) {
        fclose(writer->file);
    }
    free(writer);
}

void vm_writer_write_push(VMWriter* writer, Segment segment, int index) {
    if (!writer || !writer->file) return;
    
    const char* seg_name;
    switch (segment) {
        case SEG_CONST: seg_name = "constant"; break;
        case SEG_ARG: seg_name = "argument"; break;
        case SEG_LOCAL: seg_name = "local"; break;
        case SEG_STATIC: seg_name = "static"; break;
        case SEG_THIS: seg_name = "this"; break;
        case SEG_THAT: seg_name = "that"; break;
        case SEG_POINTER: seg_name = "pointer"; break;
        case SEG_TEMP: seg_name = "temp"; break;
        default: seg_name = "unknown";
    }
    
    fprintf(writer->file, "push %s %d\n", seg_name, index);
}

void vm_writer_write_pop(VMWriter* writer, Segment segment, int index) {
    if (!writer || !writer->file) return;
    
    const char* seg_name;
    switch (segment) {
        case SEG_CONST: seg_name = "constant"; break;
        case SEG_ARG: seg_name = "argument"; break;
        case SEG_LOCAL: seg_name = "local"; break;
        case SEG_STATIC: seg_name = "static"; break;
        case SEG_THIS: seg_name = "this"; break;
        case SEG_THAT: seg_name = "that"; break;
        case SEG_POINTER: seg_name = "pointer"; break;
        case SEG_TEMP: seg_name = "temp"; break;
        default: seg_name = "unknown";
    }
    
    fprintf(writer->file, "pop %s %d\n", seg_name, index);
}

void vm_writer_write_arithmetic(VMWriter* writer, Command command) {
    if (!writer || !writer->file) return;
    
    const char* cmd_name;
    switch (command) {
        case CMD_ADD: cmd_name = "add"; break;
        case CMD_SUB: cmd_name = "sub"; break;
        case CMD_NEG: cmd_name = "neg"; break;
        case CMD_EQ: cmd_name = "eq"; break;
        case CMD_GT: cmd_name = "gt"; break;
        case CMD_LT: cmd_name = "lt"; break;
        case CMD_AND: cmd_name = "and"; break;
        case CMD_OR: cmd_name = "or"; break;
        case CMD_NOT: cmd_name = "not"; break;
        default: cmd_name = "unknown";
    }
    
    fprintf(writer->file, "%s\n", cmd_name);
}

void vm_writer_write_label(VMWriter* writer, const char* label) {
    if (!writer || !writer->file || !label) return;
    fprintf(writer->file, "label %s\n", label);
}

void vm_writer_write_goto(VMWriter* writer, const char* label) {
    if (!writer || !writer->file || !label) return;
    fprintf(writer->file, "goto %s\n", label);
}

void vm_writer_write_if(VMWriter* writer, const char* label) {
    if (!writer || !writer->file || !label) return;
    fprintf(writer->file, "if-goto %s\n", label);
}

void vm_writer_write_call(VMWriter* writer, const char* name, int nArgs) {
    if (!writer || !writer->file || !name) return;
    fprintf(writer->file, "call %s %d\n", name, nArgs);
}

void vm_writer_write_function(VMWriter* writer, const char* name, int nLocals) {
    if (!writer || !writer->file || !name) return;
    fprintf(writer->file, "function %s %d\n", name, nLocals);
}

void vm_writer_write_return(VMWriter* writer) {
    if (!writer || !writer->file) return;
    fprintf(writer->file, "return\n");
}