#!/bin/bash

color() {
  case $2 in 
    black)
      echo -e "\033[0;30m"$1"\033[0m"
      ;;
    red)
      echo -e "\033[0;31m"$1"\033[0m"
      ;;
    green)
      echo -e "\033[0;32m"$1"\033[0m"
      ;;
    yellow)
      echo -e "\033[0;33m"$1"\033[0m"
      ;;
    blue)
      echo -e "\033[0;34m"$1"\033[0m"
      ;;
    purple)
      echo -e "\033[0;35m"$1"\033[0m"
      ;;
    cyan)
      echo -e "\033[0;36m"$1"\033[0m"
      ;;
    white)
      echo -e "\033[0;37m"$1"\033[0m"
      ;;
    *)
      echo $1
      ;;
  esac
}
