#ifndef VM_WRITER_H
#define VM_WRITER_H

#include <stdio.h>

/* VM segments */
typedef enum {
    SEG_CONST,
    SEG_ARG,
    SEG_LOCAL,
    SEG_STATIC,
    SEG_THIS,
    SEG_THAT,
    SEG_POINTER,
    SEG_TEMP
} Segment;

/* VM arithmetic commands */
typedef enum {
    CMD_ADD,
    CMD_SUB,
    CMD_NEG,
    CMD_EQ,
    CMD_GT,
    CMD_LT,
    CMD_AND,
    CMD_OR,
    CMD_NOT
} Command;

/* VM writer structure */
typedef struct {
    FILE* file;
} VMWriter;

/* Function prototypes */
VMWriter* vm_writer_new(const char* filename);
void vm_writer_close(VMWriter* writer);
void vm_writer_write_push(VMWriter* writer, Segment segment, int index);
void vm_writer_write_pop(VMWriter* writer, Segment segment, int index);
void vm_writer_write_arithmetic(VMWriter* writer, Command command);
void vm_writer_write_label(VMWriter* writer, const char* label);
void vm_writer_write_goto(VMWriter* writer, const char* label);
void vm_writer_write_if(VMWriter* writer, const char* label);
void vm_writer_write_call(VMWriter* writer, const char* name, int nArgs);
void vm_writer_write_function(VMWriter* writer, const char* name, int nLocals);
void vm_writer_write_return(VMWriter* writer);

#endif