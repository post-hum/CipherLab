{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.streamlit
    python3Packages.pandas
    python3Packages.numpy
    python3Packages.pytest
    gcc
    gnumake
  ];
  
  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH
    export PYTHONPATH=$(pwd)/src:$(pwd)/.venv/lib/python3.13/site-packages:$PYTHONPATH
    echo "CipherLab environment ready!"
    echo "Run: streamlit run app/streamlit_app.py"
  '';
}
