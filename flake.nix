{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";
  };

  outputs =
    { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      python = pkgs.python312;
    in
    {
      # Default dev shell to use native nix packages
      devShells."${system}" = {
        shell =
          let
            meteostat = python.pkgs.buildPythonPackage rec {
              pname = "meteostat";
              version = "1.7.4";

              src = pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-cV+a8V6FRXDue6WU4bxMOW2V+FNE1/gsCsqgowWFo+M=";
              };

              propagatedBuildInputs = with python.pkgs; [
                pandas
                requests
                pytz
              ];
              doCheck = false;
            };
            pygbif = python.pkgs.buildPythonPackage rec {
              pname = "pygbif";
              version = "0.6.5";

              src = pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-TqrwMtI+ruUUBh1ayQLCeMO9VNBhzVXSoCCbByqvM0M=";
              };

              propagatedBuildInputs = with python.pkgs; [
                requests
                matplotlib
                appdirs
                geomet
                shapely
              ];
              doCheck = false;
            };
          in
          pkgs.mkShell {
            buildInputs = with pkgs; [
              (python.withPackages (ps: [
                ps.pandas
                ps.numpy
                ps.sqlalchemy
                ps.psycopg2
                ps.click
                ps.tomli
                meteostat
                pygbif
              ]))
            ];
            shellHook = ''
              echo EBMS Analytics dev shell
            '';
          };

        # Python builder dev shell to use with mise ensuring cross system development
        python-builder = pkgs.mkShell {
          buildInputs = [
            pkgs.zlib
            pkgs.bzip2
            pkgs.xz
            pkgs.openssl
            pkgs.readline
            pkgs.sqlite
            pkgs.libffi
            pkgs.ncurses
            pkgs.pkg-config
            pkgs.openblas
          ];
          packages = with pkgs; [ uv ];
          shellHook = ''
            echo Python builder dev shell
            export LD_LIBRARY_PATH="${pkgs.openssl.out}/lib:${pkgs.openblas.out}/lib"
            export CPPFLAGS="-I${pkgs.openssl.dev}/include -I${pkgs.openblas.dev}/include"
            export LDFLAGS="-L${pkgs.openssl.out}/lib -L${pkgs.openblas.out}"
            export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig:${pkgs.openblas.dev}/lib/pkgconfig"

          '';
        };
        default = pkgs.mkShell {
          packages = with pkgs; [
            python312
            python312Packages.venvShellHook
            python312Packages.numpy # required to avoid import error
            uv
          ];

          venvDir = ".venv";
        };
      };

    };
}
