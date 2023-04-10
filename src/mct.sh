#!/bin/bash

function mct {
    local cmd=$1

    case $cmd in
        "init")
            mct_init
            ;;
        "getconfig")
            mct_getconfig
            ;;
        "getsecrets")
            mct_getsecrets
            ;;
        "synth")
            mct_synth
            ;;
        "deploy")
            mct_deploy
            ;;
        "destroy")
            mct_destroy
            ;;
        "*")
            echo "Usage: mct <command>"
            echo "Commands:"
            echo "  init"
            echo "  generateconfig"
            echo "  getsecrets"
            echo "  synth"
            echo "  deploy"
            echo "  destroy"
            echo "  help"
            ;;
    esac
}

function mct_init {
    echo "Initializing..."

    if [ -e "cdktf.json" ]; then
        if [ -e "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
    else
        cdktf init --template python-pip
    fi
}

function mct_getconfig {
    python3 main.py generateconfig
}

function mct_getsecrets {
    python3 main.py getsecrets
}

function mct_synth {
    python3 main.py synth
}

function mct_destroy {
    cdktf destroy
}

function mct_deploy {
    cdktf deploy
}