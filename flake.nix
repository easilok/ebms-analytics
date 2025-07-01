{
  inputs = { nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05"; };

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      # Default dev shell to use native nix packages
      devShells."${system}" = {
        default = pkgs.mkShell {
          buildInputs = with pkgs;
            [
              # uv
              (python312.withPackages
                (ps: [ ps.pandas ps.numpy ps.sqlalchemy ps.psycopg2 ps.click ps.tomli ]))
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
      };

    };
}
