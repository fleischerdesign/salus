{
  description = "salus — a health data tracker built with FastAPI, Jinja2, and HTMX";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python313
            pkgs.uv
            pkgs.ruff
            pkgs.pyright
          ];
          shellHook = ''
            echo "salus — health tracking dev environment"
            echo "python, uv, ruff, pyright available"
            echo "Run: uv run uvicorn src.salus.main:app --reload"
          '';
        };
      }
    );
}
