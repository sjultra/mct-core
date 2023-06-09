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
        if [ -e "Pipfile" ]; then
            pipenv install
        fi
    else
        cdktf init --template python
    fi
}

function mct_getconfig {
    pipenv run python main.py generateconfig
}

function mct_getsecrets {
    pipenv run python main.py getsecrets
}

function mct_synth {
    pipenv run python main.py synth
}

function mct_destroy {
    echo "Destroying..."
    tool_export_tf_variables "config.ini" "TerraformVariable"
    cdktf destroy --auto-approve
}

function mct_deploy {
    echo "Deploying..."
    tool_export_tf_variables "config.ini" "TerraformVariable"
    cdktf deploy --auto-approve
}

function tool_export_tf_variables() {
  local ini_file="$1"
  local section_name="$2"
  local section_start=0
  while IFS=' = ' read -r key value; do
    if [[ $key ]]; then
      if [[ $key == \[*] ]]; then
        if [[ "${key}" == "[$section_name]" ]]; then
          section_start=1
        else
          section_start=0
        fi
      elif [[ $value && $section_start -eq 1 ]]; then
        echo "Found Terraform variable: TF_VAR_$key"
        export "TF_VAR_$key"="$value"
      fi
    fi
  done < "$ini_file"
}