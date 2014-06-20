#!/bin/bash

_krusader-rules() 
{
	local cur prev opts pprev
	COMPREPLY=()
	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"
	opts=""
	if [[ ${prev} == krusader-rules ]] ; then
		opts="dbus"
		COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
		return 0
	fi
	if [[ ${prev} == dbus ]] ; then
	    pprev=${COMP_WORDS[COMP_CWORD-2]}
	    if [[ ${pprev} == krusader-rules ]] ; then
		opts="newLeftTab newRightTab"
		COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
	    fi
	fi
}

complete -F _krusader-rules krusader-rules