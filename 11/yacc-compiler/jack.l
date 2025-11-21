%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "y.tab.h"

extern int yylineno;
int comment_depth = 0;
%}

%x COMMENT
%x LINE_COMMENT

%%

"/*"                { BEGIN(COMMENT); comment_depth = 1; }
<COMMENT>"/*"       { comment_depth++; }
<COMMENT>"*/"       { comment_depth--; if (comment_depth == 0) BEGIN(INITIAL); }
<COMMENT>.          { /* ignore comment content */ }
<COMMENT>\n         { yylineno++; }

"//"                { BEGIN(LINE_COMMENT); }
<LINE_COMMENT>\n    { BEGIN(INITIAL); yylineno++; }
<LINE_COMMENT>.     { /* ignore comment content */ }

[ \t\r]+            { /* ignore whitespace */ }
\n                  { yylineno++; }

"class"             { return CLASS; }
"constructor"       { return CONSTRUCTOR; }
"function"          { return FUNCTION; }
"method"            { return METHOD; }
"field"             { return FIELD; }
"static"            { return STATIC; }
"var"               { return VAR; }
"int"               { return INT; }
"char"              { return CHAR; }
"boolean"           { return BOOLEAN; }
"void"              { return VOID; }
"true"              { return TRUE; }
"false"             { return FALSE; }
"null"              { return NULL_TOKEN; }
"this"              { return THIS; }
"let"               { return LET; }
"do"                { return DO; }
"if"                { return IF; }
"else"              { return ELSE; }
"while"             { return WHILE; }
"return"            { return RETURN; }

[a-zA-Z_][a-zA-Z0-9_]*  {
    yylval.string = strdup(yytext);
    return IDENTIFIER;
}

[0-9]+              {
    yylval.integer = atoi(yytext);
    return INTEGER_CONSTANT;
}

\"([^"\\]|\\.)*\"   {
    /* Remove quotes from string */
    yylval.string = strdup(yytext + 1);
    yylval.string[strlen(yylval.string) - 1] = '\0';
    return STRING_CONSTANT;
}

"{"                 { return LBRACE; }
"}"                 { return RBRACE; }
"("                 { return LPAREN; }
")"                 { return RPAREN; }
"["                 { return LBRACKET; }
"]"                 { return RBRACKET; }
"."                 { return DOT; }
","                 { return COMMA; }
";"                 { return SEMICOLON; }
"+"                 { return PLUS; }
"-"                 { return MINUS; }
"*"                 { return MULTIPLY; }
"/"                 { return DIVIDE; }
"&"                 { return AND; }
"|"                 { return OR; }
"<"                 { return LT; }
">"                 { return GT; }
"="                 { return EQ; }
"~"                 { return NOT; }

.                   {
    fprintf(stderr, "Unexpected character: %s at line %d\n", yytext, yylineno);
    return yytext[0];
}

%%

int yywrap() {
    return 1;
}
