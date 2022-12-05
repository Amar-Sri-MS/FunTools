// Created by Bertrand Serlet 2022-03-03

package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"
)

// =============== TOKEN KIND ===============

type TokenKind int

const (
	EOF           TokenKind = 0
	Punct         TokenKind = iota
	Symbol        TokenKind = iota
	Number        TokenKind = iota
	CharLiteral   TokenKind = iota
	StringLiteral TokenKind = iota
	CPPDirective  TokenKind = iota
	WhiteSpace    TokenKind = iota
)

// =============== TOKEN ===============

type Token struct {
	kind    TokenKind
	subKind int
	// for a Punct, the first character
	// for a number whether it's an int (0) or a real (1)
	// for WhiteSpace, the number of \n
	// 0 otherwise
	start int `offset of the start of the token`
	limit int `offset of the 1st character beyond token`
}

func (t Token) ToString(all string) string {
	return all[t.start:t.limit]
}
func (t Token) ToStringWithBytes(all []byte) string {
	return string(all[t.start:t.limit])
}

func (t Token) IsPunct(ch byte) bool {
	return (t.kind == Punct) && (t.limit-t.start == 1) && (t.subKind == int(ch))
}

// Whether to add a space between 2 tokens
func (t Token) NeedSpaceForPrevious(prev Token) bool {
	tk := t.kind
	pk := prev.kind
	if prev.kind == CPPDirective {
		return true
	}
	if tk == Punct {
		if IsAnyParenthesis(byte(t.subKind)) {
			return false
		}
		if IsAnyParenthesis(byte(prev.subKind)) {
			return false
		}
		if prev.kind == Symbol {
			return true
		}
		return pk == Punct // e.g. "+" "+"
	}
	if tk == StringLiteral && pk == StringLiteral {
		return true
	}
	if (tk == Symbol) || (tk == Number) {
		return (pk == Symbol) || (pk == Number)
	}
	return false
}

// =============== LEXING CONTEXT ===============

type Lexer struct {
	all   []byte `all the bytes of the current file`
	start int    `offset of the first character not yet parsed`
	line  int    `current line`
}

func (lexer Lexer) isEOL() bool {
	if lexer.start < len(lexer.all) {
		return IsNewLine(lexer.all[lexer.start])
	}
	return true // implicit EOL at EOF
}
func (lexer Lexer) isBackslashEOL() bool {
	if lexer.start+1 >= len(lexer.all) {
		return false
	}
	if lexer.all[lexer.start] != '\\' {
		return false
	}
	return IsNewLine(lexer.all[lexer.start+1])
}

// =============== BASIC CHARACTERS UTILITIES ===============

func IsDigit(ch byte) bool {
	return ch >= '0' && ch <= '9'
}
func IsHexDigit(ch byte) bool {
	return (ch >= '0' && ch <= '9') || (ch >= 'a' && ch <= 'f') || (ch >= 'A' && ch <= 'F')
}
func HexDigitValue(ch byte) (byte, bool) {
	if ch >= '0' && ch <= '9' {
		return ch - '0', true
	} else if ch >= 'a' && ch <= 'f' {
		return ch - 'a', true
	} else if ch >= 'A' && ch <= 'F' {
		return ch - 'A', true
	} else {
		return 0, false
	}
}
func IsLetter(ch byte) bool {
	return (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z')
}
func IsIdentifierStart(ch byte) bool {
	return IsLetter(ch) || ch == '_' || ch == '$'
}
func IsIdentifierChar(ch byte) bool {
	return IsIdentifierStart(ch) || IsDigit(ch)
}
func IsCommentSecondChar(ch byte) bool {
	return (ch == '/') || (ch == '*')
}
func IsNewLine(ch byte) bool {
	return ch == '\n' || ch == '\r'
}
func IsAnyParenthesis(ch byte) bool {
	return ch == '(' || ch == ')' || ch == '[' || ch == ']' || ch == '{' || ch == '}'
}

// =============== LEXING CONTEXT MUTATORS ===============

func (lexer *Lexer) skipRestOfLine() {
	for lexer.start < len(lexer.all) {
		if lexer.isEOL() {
			lexer.start++
			lexer.line++
			return
		}
		if lexer.isBackslashEOL() {
			lexer.start++
			lexer.line++
			return
		}
		lexer.start++
	}
}
func (lexer *Lexer) skipUntilCloseComment() {
	for lexer.start < len(lexer.all) {
		ch := lexer.all[lexer.start]
		if (ch == '*') && lexer.start+1 < len(lexer.all) && (lexer.all[lexer.start+1] == '/') {
			lexer.start += 2
			return
		}
		if lexer.isEOL() {
			lexer.line++
		}
		lexer.start++
	}
}
func (lexer *Lexer) SkipWhiteSpace() {
	ll := len(lexer.all)
	for lexer.start < ll {
		ch := lexer.all[lexer.start]
		switch ch {
		case 0:
			return
		case ' ', '\t', '\f':
			lexer.start++
		case '\n', '\r':
			lexer.start++
			lexer.line++
		case '\\':
			if lexer.isBackslashEOL() {
				lexer.start += 2
				lexer.line++
			}
		case '/':
			if lexer.start+1 >= ll {
				return
			}
			next := lexer.all[lexer.start+1]
			if next == '/' {
				lexer.start += 2
				lexer.skipRestOfLine()
			} else if next == '*' {
				lexer.start += 2
				lexer.skipUntilCloseComment()
			} else {
				return
			}
		default:
			return
		}
	}
}
func (lexer *Lexer) finishCPPDirective() {
	for lexer.start < len(lexer.all) {
		ch := lexer.all[lexer.start]
		lexer.start++
		switch ch {
		case '\n', '\r':
			lexer.start-- // exclude the '\n'
			return        // do not include the '\n'
		case '\\':
			if lexer.start >= len(lexer.all) {
				return
			}
			ch = lexer.all[lexer.start]
			lexer.start++
			if IsNewLine(ch) {
				lexer.line++
			}
		case '\'':
			lexer.finishCharLiteral()
		case '"':
			lexer.finishStringLiteral()
		case '/': // either /= or just / or a comment
			if lexer.start >= len(lexer.all) {
				return
			}
			ch = lexer.all[lexer.start]
			if ch == '*' {
				lexer.start++
				lexer.skipUntilCloseComment()
			} else if ch == '/' {
				lexer.start++
				lexer.skipRestOfLine()
				// undo the \n
				if lexer.all[lexer.start-1] == '\n' {
					// do not include the '\n'
					lexer.start--
					lexer.line--
				}
				return
			}
		default:
		}
	}
}
func (lexer *Lexer) finishSymbol() {
	for lexer.start < len(lexer.all) {
		ch := lexer.all[lexer.start]
		if !IsIdentifierChar(ch) {
			return
		}
		lexer.start++
	}
}
func (lexer *Lexer) consumeDigits() {
	pl := len(lexer.all)
	for lexer.start < pl {
		if !IsDigit(lexer.all[lexer.start]) {
			return
		}
		lexer.start++
	}
}
func (lexer *Lexer) consumeHexDigits() {
	pl := len(lexer.all)
	for lexer.start < pl {
		if !IsHexDigit(lexer.all[lexer.start]) {
			return
		}
		lexer.start++
	}
}
func (lexer *Lexer) tokenizeNumber() Token {
	var t Token
	pl := len(lexer.all)
	t.start = lexer.start
	t.kind = Number
	t.subKind = 0
	ch := lexer.all[lexer.start]
	if ch == '0' && (lexer.start+1 < pl) && (lexer.all[lexer.start+1] == 'x') {
		// it's a hex number
		lexer.start += 2
		lexer.consumeHexDigits()
		goto potentialSuffix
	}
	if ch == '.' {
		t.subKind = 1
	} // real
	lexer.start++
	lexer.consumeDigits()
	if lexer.start >= pl {
		goto done
	}
	ch = lexer.all[lexer.start]
	if t.subKind == 0 && ch == '.' {
		t.subKind = 1
		lexer.start++
		lexer.consumeDigits()
		if lexer.start >= pl {
			goto done
		}
		ch = lexer.all[lexer.start]
	}
	if ch == 'e' || ch == 'E' {
		t.subKind = 1
		lexer.start++
		if lexer.start >= pl {
			goto done
		}
		ch = lexer.all[lexer.start]
		if ch == '+' || ch == '-' {
			lexer.start++
		}
		lexer.consumeDigits()
	}
	if t.subKind == 1 {
		goto done
	}
potentialSuffix:
	for {
		if lexer.start >= pl {
			goto done
		}
		switch lexer.all[lexer.start] {
		case 'u', 'U', 'l', 'L':
			lexer.start++
		case 'f', 'F':
			t.subKind = 1
			lexer.start++
		default:
			goto done
		}
	}
done:
	t.limit = lexer.start
	return t
}
func (lexer *Lexer) tokenizeCharLiteral() Token {
	var t Token
	t.kind = CharLiteral
	t.start = lexer.start
	lexer.start++
	lexer.finishCharLiteral()
	t.limit = lexer.start
	return t
}

// Assumes we've already swallowed the initial '
func (lexer *Lexer) finishCharLiteral() {
	for lexer.start < len(lexer.all) {
		ch := lexer.all[lexer.start]
		if ch == '\'' {
			lexer.start++
			return
		}
		if ch == '\\' {
			lexer.start++
			if lexer.start >= len(lexer.all) {
				break
			}
		}
		lexer.start++
	}
}

// Assumes we've already swallowed the initial "
func (lexer *Lexer) finishStringLiteral() {
	for lexer.start < len(lexer.all) {
		ch := lexer.all[lexer.start]
		if ch == '"' {
			lexer.start++
			return
		}
		if lexer.isBackslashEOL() {
			lexer.start += 2
			lexer.line++
			continue
		}
		if ch == '\\' {
			lexer.start++
			if lexer.start >= len(lexer.all) {
				break
			}
		}
		if IsNewLine(ch) {
			lexer.line++
		}
		lexer.start++
	}
}
func (lexer *Lexer) tokenizeStringLiteral() Token {
	var t Token
	t.kind = StringLiteral
	t.start = lexer.start
	lexer.start++
	lexer.finishStringLiteral()
	t.limit = lexer.start
	return t
}
func (lexer *Lexer) tokenizeSymbol() Token {
	// Assumes we have an identifier start
	t := Token{start: lexer.start, kind: Symbol}
	lexer.start++
	lexer.finishSymbol()
	t.limit = lexer.start
	return t
}
func (lexer *Lexer) tokenizeCPPDirective() Token {
	// Assumes we have # followed by a proper directive
	t := Token{start: lexer.start, kind: CPPDirective}
	lexer.start++ // skip #
	lexer.SkipWhiteSpace()
	savedStart := lexer.start
	t2 := lexer.Tokenize()
	if t2.kind != Symbol {
		lexer.start = savedStart // backtrack
	} else {
		t.subKind = 0 // TODO: was : int(CPPDirSubKindFromString(t2.ToStringWithBytes(lexer.all)))
	}
	lexer.finishCPPDirective()
	t.limit = lexer.start
	return t
}
func (lexer *Lexer) tokenizePunct(nchars int) Token {
	// Assumes we have seen some multi-char punctuation
	t := Token{start: lexer.start, kind: Punct, subKind: int(lexer.all[lexer.start])}
	lexer.start += nchars
	t.limit = t.start + nchars
	return t
}
func (lexer *Lexer) tokenizeWhiteSpace() Token {
	// Assumes we have seen a white space starter
	origLine := lexer.line
	start := lexer.start
	lexer.SkipWhiteSpace()
	t := Token{start: start, kind: WhiteSpace, subKind: lexer.line - origLine, limit: lexer.start}
	return t
}
func (lexer *Lexer) nextChar() byte {
	if lexer.start+1 < len(lexer.all) { // one more char after
		return lexer.all[lexer.start+1]
	}
	return 0
}
func (lexer *Lexer) nextNextChar() byte {
	if lexer.start+2 < len(lexer.all) { // one more char after
		return lexer.all[lexer.start+2]
	}
	return 0
}
func (lexer *Lexer) Tokenize() Token {
	ll := len(lexer.all)
	if lexer.start >= ll {
		return Token{start: lexer.start, kind: EOF, limit: 0}
	}
	ch := lexer.all[lexer.start]
	switch ch {
	case ' ', '\t', '\f', '\n', '\r':
		return lexer.tokenizeWhiteSpace()
	case '\'':
		return lexer.tokenizeCharLiteral()
	case '"':
		return lexer.tokenizeStringLiteral()
	case '0', '1', '2', '3', '4', '5', '6', '7', '8', '9':
		return lexer.tokenizeNumber()
	case '.': // can be number or '...' or just '.'
		ch2 := lexer.nextChar()
		if IsDigit(ch2) {
			return lexer.tokenizeNumber()
		} else if ch2 == '.' && lexer.nextNextChar() == '.' { //...
			return lexer.tokenizePunct(3) // ...
		}
	case '<', '>', '&', '|': // either (for <): <<=, <=, << or just <
		ch2 := lexer.nextChar()
		if ch2 == ch {
			if lexer.nextNextChar() == '=' {
				return lexer.tokenizePunct(3) // <<= or >>= or &&= or ||=
			}
			return lexer.tokenizePunct(2) // << or >> or && or ||
		} else if ch2 == '=' {
			return lexer.tokenizePunct(2) // <= or >= or &= or |=
		}
	case '+', '-': // either (for +) ++, +=, or just +
		ch2 := lexer.nextChar()
		if ch2 == ch || ch2 == '=' {
			return lexer.tokenizePunct(2) // ++ or -- or += or -=
		}
	case '^', '%', '*', '=': // either (for ^) ^= or just ^
		if lexer.nextChar() == '=' {
			return lexer.tokenizePunct(2) // ^= or -%= or *= or /=
		}
	case '!':
		ch2 := lexer.nextChar()
		if ch2 == '=' {
			return lexer.tokenizePunct(2) // !=
		}
	case '#':
		{
			return lexer.tokenizeCPPDirective()
		}
	case '/': // either /= or just / or a comment
		ch2 := lexer.nextChar()
		if IsCommentSecondChar(ch2) {
			return lexer.tokenizeWhiteSpace()
		} else if lexer.nextChar() == '=' {
			return lexer.tokenizePunct(2) // /=
		}
	case 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
		'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
		'_', '$':
		return lexer.tokenizeSymbol()
	case '\\':
		if IsNewLine(lexer.nextChar()) {
			return lexer.tokenizeWhiteSpace()
		}
	case '(', ')', '[', ']', '{', '}', ',', ';', ':', '@', '?', '~', '`':
	default:
		// We have a strange character.  We make it a punctuation for fidelity
	}
	// in all other cases:
	return lexer.tokenizePunct(1)
}

func (lexer Lexer) PeekToken() Token {
	lexer.SkipWhiteSpace()
	return lexer.Tokenize()
}

// =============== OUTPUT ===============

type Output struct {
	expanded []byte `all the output bytes`
}

// Convert the whole output to a string
func (output *Output) ToString() string {
	return string(output.expanded)
}

func (output *Output) AppendString(str string) {
	for _, ch := range str {
		output.expanded = append(output.expanded, byte(ch))
	}
}
func (output *Output) AppendTokenBytesWithLexer(lexer Lexer, t Token) {
	output.expanded = append(output.expanded, lexer.all[t.start:t.limit]...)
}

// =============== FILES ===============

func ReadFileToBytes(path string) ([]byte, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	return ioutil.ReadAll(file)
}

func StripFileOfComments(path string, output *Output, yaml_output bool) {
	all, err := ReadFileToBytes(path)
	if err != nil {
		log.Fatal(err)
	}
	lexer := Lexer{all: all, start: 0, line: 1}
	prevIsNewLine := true
	prev := Token{}
	// Total hack because gcc does something funky inside enums and structs with whitespace
	specialCase := 0
	for {
		t := lexer.Tokenize()
		if t.kind == EOF {
			break
		}
		if t.kind == CPPDirective {
			prev = t
			continue
		}
		if t.kind == Punct && (t.subKind == ',' || t.subKind == ';') {
			output.AppendTokenBytesWithLexer(lexer, t)
			continue
		}
		if t.kind == WhiteSpace {
			lastIsNewLine := IsNewLine(lexer.all[t.limit-1])
			if specialCase == 2 {
				lastIsNewLine = false
			}
			if lastIsNewLine {
				if !prevIsNewLine {
					output.AppendString("\n")
					prevIsNewLine = true
					prev = t
				}
			} else {
				nextToken := lexer.PeekToken()
				if nextToken.kind != WhiteSpace && nextToken.NeedSpaceForPrevious(prev) {
					output.AppendString(" ")
					prev = t
				}
				prevIsNewLine = false
			}
			continue
		}

		if yaml_output && prevIsNewLine == true {
			output.AppendString("  - ")
		}

		if specialCase == 0 && t.kind == Symbol && (t.ToStringWithBytes(all) == "enum" || t.ToStringWithBytes(all) == "struct" || t.ToStringWithBytes(all) == "union") {
			specialCase = 1
		}
		if specialCase == 1 && t.IsPunct('{') {
			output.AppendString(" ")
			specialCase = 2
		}
		if specialCase == 2 && t.IsPunct('}') {
			specialCase = 0
		}
		output.AppendTokenBytesWithLexer(lexer, t)
		prevIsNewLine = false
		prev = t
	}
}

func printStrippedFile(path string, rel string, yaml_output bool) {
	output := Output{}

	if yaml_output {
		// yaml key
		output.AppendString(rel)
		output.AppendString(":\n")
	} else {
		output.AppendString("//--------------\n\n")
		output.AppendString("//")
		output.AppendString(rel)
		output.AppendString(": \n\n")
	}

	StripFileOfComments(path, &output, yaml_output)
	fmt.Println(output.ToString())
}

func walkDir(dir string, yaml_output bool) {
	filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			fmt.Println(err)
			return nil
		}
		if !info.IsDir() && filepath.Ext(path) == ".h" {
			printStrippedFile(path, strings.TrimPrefix(path, dir+"/"), yaml_output)
		}
		return nil
	})
}

// =============== MAIN ===============

func main() {
	yaml_output := false
	if len(os.Args) <= 1 {
		fmt.Println("API Summarizer: Need to specify directory that has the .h files")
		fmt.Println("Usage:")
		fmt.Println("	go run main.go <path to .h files> [-y]")
		fmt.Println("	-y (optional): output in yaml format")
		log.Fatal("")
	} else {
		// check the 2nd argument is -y
		if len(os.Args) > 2 && os.Args[2] == "-y" {
			yaml_output = true
		}
		walkDir(os.Args[1], yaml_output)
	}
}
