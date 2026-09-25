"""
Vyom - Coding Languages Knowledge
Vyom ki asli coding "knowledge" LLM se aati hai. Ye module sirf structured
metadata (extension, paradigm, comment-style, linter) + language-detection deta hai.
"""

LANGUAGE_REGISTRY = {
    "Python":       {"ext": ".py",    "paradigm": "multi-paradigm",     "comment": "#",   "linter": "pylint/ruff",     "formatter": "black"},
    "JavaScript":   {"ext": ".js",    "paradigm": "multi-paradigm",     "comment": "//",  "linter": "eslint",          "formatter": "prettier"},
    "TypeScript":   {"ext": ".ts",    "paradigm": "multi-paradigm",     "comment": "//",  "linter": "eslint",          "formatter": "prettier"},
    "Java":         {"ext": ".java",  "paradigm": "object-oriented",    "comment": "//",  "linter": "checkstyle",      "formatter": "google-java-format"},
    "C":            {"ext": ".c",     "paradigm": "procedural",         "comment": "//",  "linter": "cppcheck",        "formatter": "clang-format"},
    "C++":          {"ext": ".cpp",   "paradigm": "multi-paradigm",     "comment": "//",  "linter": "cppcheck",        "formatter": "clang-format"},
    "C#":           {"ext": ".cs",    "paradigm": "object-oriented",    "comment": "//",  "linter": "roslyn-analyzers","formatter": "dotnet-format"},
    "Go":           {"ext": ".go",    "paradigm": "procedural",         "comment": "//",  "linter": "golint",          "formatter": "gofmt"},
    "Rust":         {"ext": ".rs",    "paradigm": "multi-paradigm",     "comment": "//",  "linter": "clippy",          "formatter": "rustfmt"},
    "Ruby":         {"ext": ".rb",    "paradigm": "object-oriented",    "comment": "#",   "linter": "rubocop",         "formatter": "rubocop"},
    "PHP":          {"ext": ".php",   "paradigm": "multi-paradigm",     "comment": "//",  "linter": "phpcs",           "formatter": "php-cs-fixer"},
    "Swift":        {"ext": ".swift", "paradigm": "multi-paradigm",     "comment": "//",  "linter": "swiftlint",       "formatter": "swiftformat"},
    "Kotlin":       {"ext": ".kt",    "paradigm": "multi-paradigm",     "comment": "//",  "linter": "ktlint",          "formatter": "ktlint"},
    "Scala":        {"ext": ".scala", "paradigm": "functional/OOP",     "comment": "//",  "linter": "scalastyle",      "formatter": "scalafmt"},
    "R":            {"ext": ".r",     "paradigm": "functional",         "comment": "#",   "linter": "lintr",           "formatter": "styler"},
    "MATLAB":       {"ext": ".m",     "paradigm": "procedural",         "comment": "%",   "linter": "mlint",           "formatter": "-"},
    "Perl":         {"ext": ".pl",    "paradigm": "procedural",         "comment": "#",   "linter": "perlcritic",      "formatter": "perltidy"},
    "Haskell":      {"ext": ".hs",    "paradigm": "functional",         "comment": "--",  "linter": "hlint",           "formatter": "ormolu"},
    "Lua":          {"ext": ".lua",   "paradigm": "procedural",         "comment": "--",  "linter": "luacheck",        "formatter": "stylua"},
    "Dart":         {"ext": ".dart",  "paradigm": "object-oriented",    "comment": "//",  "linter": "dart-analyze",    "formatter": "dartfmt"},
    "Objective-C":  {"ext": ".m",     "paradigm": "object-oriented",    "comment": "//",  "linter": "oclint",          "formatter": "clang-format"},
    "Shell/Bash":   {"ext": ".sh",    "paradigm": "scripting",          "comment": "#",   "linter": "shellcheck",      "formatter": "shfmt"},
    "PowerShell":   {"ext": ".ps1",   "paradigm": "scripting",          "comment": "#",   "linter": "PSScriptAnalyzer","formatter": "-"},
    "SQL":          {"ext": ".sql",   "paradigm": "declarative",        "comment": "--",  "linter": "sqlfluff",        "formatter": "sqlfluff"},
    "HTML":         {"ext": ".html",  "paradigm": "markup",             "comment": "<!--","linter": "htmlhint",        "formatter": "prettier"},
    "CSS":          {"ext": ".css",   "paradigm": "declarative",        "comment": "/*",  "linter": "stylelint",       "formatter": "prettier"},
    "Julia":        {"ext": ".jl",    "paradigm": "multi-paradigm",     "comment": "#",   "linter": "-",               "formatter": "JuliaFormatter"},
    "Elixir":       {"ext": ".ex",    "paradigm": "functional",         "comment": "#",   "linter": "credo",           "formatter": "mix format"},
    "Erlang":       {"ext": ".erl",   "paradigm": "functional",         "comment": "%",   "linter": "elvis",           "formatter": "-"},
    "Clojure":      {"ext": ".clj",   "paradigm": "functional",         "comment": ";",   "linter": "clj-kondo",       "formatter": "cljfmt"},
    "F#":           {"ext": ".fs",    "paradigm": "functional",         "comment": "//",  "linter": "-",               "formatter": "fantomas"},
    "VB.NET":       {"ext": ".vb",    "paradigm": "object-oriented",    "comment": "'",   "linter": "-",               "formatter": "-"},
    "Assembly":     {"ext": ".asm",   "paradigm": "low-level",          "comment": ";",   "linter": "-",               "formatter": "-"},
    "COBOL":        {"ext": ".cbl",   "paradigm": "procedural",         "comment": "*",   "linter": "-",               "formatter": "-"},
    "Fortran":      {"ext": ".f90",   "paradigm": "procedural",         "comment": "!",   "linter": "-",               "formatter": "-"},
    "Groovy":       {"ext": ".groovy","paradigm": "multi-paradigm",     "comment": "//",  "linter": "codenarc",        "formatter": "-"},
    "Solidity":     {"ext": ".sol",   "paradigm": "object-oriented",    "comment": "//",  "linter": "solhint",         "formatter": "prettier-plugin-solidity"},
    "Zig":          {"ext": ".zig",   "paradigm": "procedural",         "comment": "//",  "linter": "-",               "formatter": "zig fmt"},
    "Nim":          {"ext": ".nim",   "paradigm": "multi-paradigm",     "comment": "#",   "linter": "-",               "formatter": "-"},
    "Crystal":      {"ext": ".cr",    "paradigm": "object-oriented",    "comment": "#",   "linter": "ameba",           "formatter": "crystal tool format"},
    "OCaml":        {"ext": ".ml",    "paradigm": "functional",         "comment": "(*",  "linter": "-",               "formatter": "ocamlformat"},
    "Racket":       {"ext": ".rkt",   "paradigm": "functional",         "comment": ";",   "linter": "-",               "formatter": "-"},
    "Scheme":       {"ext": ".scm",   "paradigm": "functional",         "comment": ";",   "linter": "-",               "formatter": "-"},
    "Prolog":       {"ext": ".plg",   "paradigm": "logic",              "comment": "%",   "linter": "-",               "formatter": "-"},
    "Ada":          {"ext": ".adb",   "paradigm": "procedural",         "comment": "--",  "linter": "-",               "formatter": "-"},
    "Pascal":       {"ext": ".pas",   "paradigm": "procedural",         "comment": "//",  "linter": "-",               "formatter": "-"},
    "D":            {"ext": ".d",     "paradigm": "multi-paradigm",     "comment": "//",  "linter": "-",               "formatter": "dfmt"},
    "Elm":          {"ext": ".elm",   "paradigm": "functional",         "comment": "--",  "linter": "elm-analyse",     "formatter": "elm-format"},
    "YAML":         {"ext": ".yaml",  "paradigm": "data/config",        "comment": "#",   "linter": "yamllint",        "formatter": "prettier"},
    "JSON":         {"ext": ".json",  "paradigm": "data",               "comment": "-",   "linter": "jsonlint",        "formatter": "prettier"},
    "TOML":         {"ext": ".toml",  "paradigm": "data/config",        "comment": "#",   "linter": "-",               "formatter": "taplo"},
    "GraphQL":      {"ext": ".graphql","paradigm":"declarative/query",  "comment": "#",   "linter": "graphql-eslint",  "formatter": "prettier"},
    "Terraform/HCL":{"ext": ".tf",    "paradigm": "declarative/IaC",    "comment": "#",   "linter": "tflint",          "formatter": "terraform fmt"},
    "Verilog":      {"ext": ".v",     "paradigm": "hardware-description","comment": "//", "linter": "verilator",       "formatter": "-"},
    "VHDL":         {"ext": ".vhd",   "paradigm": "hardware-description","comment": "--", "linter": "-",               "formatter": "-"},
    "Delphi/Object Pascal": {"ext": ".pas",  "paradigm": "object-oriented",     "comment": "//",  "linter": "-", "formatter": "-"},
    "Lisp":                 {"ext": ".lisp", "paradigm": "functional",          "comment": ";",   "linter": "-", "formatter": "-"},
    "Common Lisp":           {"ext": ".lisp", "paradigm": "multi-paradigm",      "comment": ";",   "linter": "sbcl-lint", "formatter": "-"},
    "GDScript":              {"ext": ".gd",   "paradigm": "object-oriented",     "comment": "#",   "linter": "-", "formatter": "gdformat"},
    "V":                     {"ext": ".v",    "paradigm": "procedural",          "comment": "//",  "linter": "-", "formatter": "v fmt"},
    "Haxe":                  {"ext": ".hx",   "paradigm": "multi-paradigm",      "comment": "//",  "linter": "-", "formatter": "-"},
    "Tcl":                   {"ext": ".tcl",  "paradigm": "scripting",           "comment": "#",   "linter": "-", "formatter": "-"},
    "ABAP":                  {"ext": ".abap", "paradigm": "procedural",          "comment": "*",   "linter": "-", "formatter": "-"},
    "PL/SQL":                {"ext": ".pls",  "paradigm": "procedural/declarative","comment": "--","linter": "-", "formatter": "-"},
    "T-SQL":                 {"ext": ".sql",  "paradigm": "declarative",         "comment": "--",  "linter": "sqlfluff", "formatter": "sqlfluff"},
    "PL/pgSQL":              {"ext": ".sql",  "paradigm": "procedural/declarative","comment": "--","linter": "-", "formatter": "-"},
    "Visual Basic":          {"ext": ".bas",  "paradigm": "object-oriented",     "comment": "'",   "linter": "-", "formatter": "-"},
    "Smalltalk":             {"ext": ".st",   "paradigm": "object-oriented",     "comment": "\"",  "linter": "-", "formatter": "-"},
    "BASIC":                 {"ext": ".bas",  "paradigm": "procedural",          "comment": "REM", "linter": "-", "formatter": "-"},
    "Forth":                 {"ext": ".fs",   "paradigm": "stack-based",         "comment": "\\",  "linter": "-", "formatter": "-"},
    "Logo":                  {"ext": ".logo", "paradigm": "educational/procedural","comment": ";", "linter": "-", "formatter": "-"},
    "ALGOL":                 {"ext": ".alg",  "paradigm": "procedural",          "comment": "comment", "linter": "-", "formatter": "-"},
    "APL":                   {"ext": ".apl",  "paradigm": "array-programming",   "comment": "note",   "linter": "-", "formatter": "-"},
    "Simula":                {"ext": ".sim",  "paradigm": "object-oriented",     "comment": "!",   "linter": "-", "formatter": "-"},
    "Modula-2":              {"ext": ".mod",  "paradigm": "procedural",          "comment": "(*",  "linter": "-", "formatter": "-"},
    "Chapel":                {"ext": ".chpl", "paradigm": "parallel/procedural", "comment": "//",  "linter": "-", "formatter": "-"},
    "PureScript":            {"ext": ".purs", "paradigm": "functional",          "comment": "--",  "linter": "-", "formatter": "purty"},
    "Reason":                {"ext": ".re",   "paradigm": "functional/OOP",      "comment": "//",  "linter": "-", "formatter": "refmt"},
    "ReScript":              {"ext": ".res",  "paradigm": "functional",          "comment": "//",  "linter": "-", "formatter": "rescript format"},
    "CoffeeScript":          {"ext": ".coffee","paradigm": "scripting",          "comment": "#",   "linter": "coffeelint", "formatter": "-"},
    "ActionScript":          {"ext": ".as",   "paradigm": "object-oriented",     "comment": "//",  "linter": "-", "formatter": "-"},
    "ColdFusion":            {"ext": ".cfm",  "paradigm": "scripting",           "comment": "cfcomment","linter": "-", "formatter": "-"},
    "Apex":                  {"ext": ".cls",  "paradigm": "object-oriented",     "comment": "//",  "linter": "pmd", "formatter": "-"},
    "SystemVerilog":         {"ext": ".sv",   "paradigm": "hardware-description","comment": "//",  "linter": "verilator", "formatter": "-"},
    "OpenCL C":              {"ext": ".cl",   "paradigm": "parallel/procedural", "comment": "//",  "linter": "-", "formatter": "clang-format"},
    "CUDA C++":              {"ext": ".cu",   "paradigm": "parallel/procedural", "comment": "//",  "linter": "-", "formatter": "clang-format"},
    "Mojo":                  {"ext": ".mojo", "paradigm": "multi-paradigm (AI/ML)","comment": "#", "linter": "-", "formatter": "-"},
    "Carbon":                {"ext": ".carbon","paradigm": "multi-paradigm (experimental)","comment": "//", "linter": "-", "formatter": "-"},
    "Datalog":               {"ext": ".dl",   "paradigm": "declarative/logic",   "comment": "note2",   "linter": "-", "formatter": "-"},
    "Mercury":               {"ext": ".mer",    "paradigm": "logic/functional",    "comment": "note2",   "linter": "-", "formatter": "-"},
    "Wolfram Language":      {"ext": ".wl",   "paradigm": "symbolic/functional", "comment": "(*",  "linter": "-", "formatter": "-"},
    "SAS":                   {"ext": ".sas",  "paradigm": "procedural (statistics)","comment": "*", "linter": "-", "formatter": "-"},
    "Q#":                    {"ext": ".qs",   "paradigm": "quantum computing",   "comment": "//",  "linter": "-", "formatter": "-"},
    "LabVIEW":               {"ext": ".vi",   "paradigm": "graphical/dataflow",  "comment": "-",   "linter": "-", "formatter": "-"},
    "Pro*C":                 {"ext": ".pc",   "paradigm": "procedural (embedded SQL)","comment": "//", "linter": "-", "formatter": "-"},
    "X10":                   {"ext": ".x10",  "paradigm": "parallel/object-oriented","comment": "//","linter": "-", "formatter": "-"},
    "Pony":                  {"ext": ".pony", "paradigm": "actor-model/object-oriented","comment": "//","linter": "-", "formatter": "-"},
    "Vala":                  {"ext": ".vala", "paradigm": "object-oriented",     "comment": "//",  "linter": "-", "formatter": "-"},
    "Odin":                  {"ext": ".odin", "paradigm": "procedural/systems",  "comment": "//",  "linter": "-", "formatter": "-"},
    "Jai":                   {"ext": ".jai",  "paradigm": "systems (beta)",      "comment": "//",  "linter": "-", "formatter": "-"},
    "Hare":                  {"ext": ".ha",   "paradigm": "systems",             "comment": "//",  "linter": "-", "formatter": "-"},
    "Gleam":                 {"ext": ".gleam","paradigm": "functional (BEAM)",   "comment": "//",  "linter": "-", "formatter": "gleam format"},
    "Roc":                   {"ext": ".roc",  "paradigm": "functional",          "comment": "#",   "linter": "-", "formatter": "roc format"},
    "Unison":                {"ext": ".u",    "paradigm": "functional",          "comment": "--",  "linter": "-", "formatter": "-"},
    "Ballerina":             {"ext": ".bal",  "paradigm": "concurrent/cloud-native","comment": "//","linter": "-", "formatter": "bal format"},
    "Hack":                  {"ext": ".hack", "paradigm": "object-oriented",     "comment": "//",  "linter": "hhast", "formatter": "hackfmt"},
}


def detect_language_from_filename(filename):
    filename = filename.lower()
    for lang, meta in LANGUAGE_REGISTRY.items():
        if filename.endswith(meta["ext"]):
            return lang
    return None


def detect_language_from_code(code):
    signatures = [
        ("Python", ["def ", "import ", "elif ", "self.", ":\n"]),
        ("JavaScript", ["function ", "const ", "let ", "=>", "console.log"]),
        ("TypeScript", ["interface ", ": string", ": number", "implements "]),
        ("Java", ["public class ", "public static void main", "System.out.println"]),
        ("C++", ["#include <iostream>", "std::", "cout <<"]),
        ("C", ["#include <stdio.h>", "printf(", "int main("]),
        ("Go", ["package main", "func main()", "fmt.Println"]),
        ("Rust", ["fn main()", "let mut ", "println!"]),
        ("Ruby", ["def ", "end\n", "puts "]),
        ("PHP", ["<?php", "echo ", "$"]),
        ("Swift", ["func ", "var ", "let ", "import Foundation"]),
        ("Kotlin", ["fun main(", "val ", "println("]),
        ("SQL", ["SELECT ", "FROM ", "WHERE ", "INSERT INTO"]),
        ("Shell/Bash", ["#!/bin/bash", "#!/bin/sh", "echo $"]),
        ("HTML", ["<!DOCTYPE html>", "<html", "<div"]),
        ("CSS", ["{", "px;", "color:"]),
        ("Elixir", ["defmodule ", "def ", "|> ", "IO.puts"]),
        ("Haskell", ["::", "-> ", "main = "]),
        ("Lua", ["local ", "function ", "end\n"]),
        ("CoffeeScript", ["->", "class ", "@"]),
        ("Perl", ["my $", "use strict", "print "]),
        ("R", ["<-", "function(", "library("]),
    ]

    scores = {}
    for lang, keywords in signatures:
        score = sum(1 for kw in keywords if kw in code)
        if score > 0:
            scores[lang] = score

    if not scores:
        return None
    return max(scores, key=scores.get)


def get_language_metadata(language):
    return LANGUAGE_REGISTRY.get(language)


def list_supported_languages():
    return sorted(LANGUAGE_REGISTRY.keys())
