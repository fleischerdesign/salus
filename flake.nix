{
  description = "salus — a health data tracker built with FastAPI and SvelteKit";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
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
        lib = nixpkgs.lib;
        python = pkgs.python313;
        pythonEnv = python.withPackages (
          ps: with ps; [
            fastapi
            uvicorn
            sqlmodel
            python-multipart
            pydantic-settings
            python-jose
            authlib
            ldap3
            bcrypt
          ]
        );
      in
      {
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "salus";
          version = "0.1.0";
          src = ./.;
          nativeBuildInputs = [ pkgs.makeWrapper ];
          buildInputs = [ pythonEnv ];
          installPhase = ''
            mkdir -p $out/lib/salus $out/bin
            cp -r src $out/lib/salus/
            cp pyproject.toml $out/lib/salus/
            mkdir -p $out/lib/salus/frontend
            cp -r ${self.packages.${system}.frontend} $out/lib/salus/frontend/build

            makeWrapper ${pythonEnv}/bin/uvicorn $out/bin/salus \
              --set PYTHONPATH "$out/lib/salus/src" \
              --add-flags "salus.main:app --host 0.0.0.0 --port ''${PORT:-8000}"
          '';
        };

        packages.dockerImage = pkgs.dockerTools.buildLayeredImage {
          name = "ghcr.io/fleischerdesign/salus";
          tag = "latest";
          contents = [
            self.packages.${system}.default
            pkgs.dumb-init
            pkgs.curl
          ];
          config = {
            Cmd = [
              "${pkgs.dumb-init}/bin/dumb-init"
              "--"
              "${self.packages.${system}.default}/bin/salus"
            ];
            Expose = { "8000/tcp" = { }; };
            Volumes = { "/data" = { }; };
            Env = [
              "SALUS_DATABASE_URL=sqlite:///data/salus.db"
            ];
          };
        };

        packages.frontend = pkgs.buildNpmPackage {
          pname = "salus-frontend";
          version = "0.1.0";
          src = ./frontend;
          npmDepsHash = "sha256-6eOjzzALkIUzujIP4bv13v4FS0KS7fvgLiojUTKhpTw=";
          installPhase = ''
            runHook preInstall
            mkdir -p $out
            cp -r build/* $out/
            runHook postInstall
          '';
        };

        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python313
            pkgs.uv
            pkgs.ruff
            pkgs.pyright
            pkgs.nodejs_22
          ];
          shellHook = ''
            echo "salus — health tracking dev environment"
            echo "python, uv, ruff, pyright, node available"
            echo "Backend:  uv run uvicorn src.salus.main:app --reload"
            echo "Frontend: cd frontend && npm run dev"
          '';
        };
      }
    )
    // {
      overlays.default = final: _: {
        salus = self.packages.${final.stdenv.hostPlatform.system}.default;
      };

      nixosModules.default =
        {
          config,
          lib,
          pkgs,
          ...
        }:
        let
          cfg = config.services.salus;
        in
        {
          options.services.salus = {
            enable = lib.mkEnableOption "Salus health data tracker";
            package = lib.mkPackageOption pkgs "salus" { };
            port = lib.mkOption {
              type = lib.types.port;
              default = 8200;
              description = "Port to listen on.";
            };
            databaseUrl = lib.mkOption {
              type = lib.types.str;
              default = "sqlite:///var/lib/salus/salus.db";
              description = "Database connection URL (SQLite or PostgreSQL).";
            };
            jwtSecretFile = lib.mkOption {
              type = lib.types.nullOr lib.types.path;
              default = null;
              description = "Environment file containing SALUS_JWT_SECRET_KEY.";
            };
            openFirewall = lib.mkOption {
              type = lib.types.bool;
              default = false;
              description = "Open the configured port in the firewall.";
            };
          };

          config = lib.mkIf cfg.enable {
            networking.firewall = lib.mkIf cfg.openFirewall {
              allowedTCPPorts = [ cfg.port ];
            };

            systemd.services.salus = {
              description = "Salus Health Data Tracker";
              after = [ "network.target" ];
              wantedBy = [ "multi-user.target" ];
              serviceConfig = {
                DynamicUser = true;
                StateDirectory = "salus";
                WorkingDirectory = "/var/lib/salus";
                ExecStart = "${lib.getExe cfg.package}";
                Restart = "on-failure";
                Environment = [
                  "PORT=${toString cfg.port}"
                  "SALUS_DATABASE_URL=${cfg.databaseUrl}"
                ];
              } // lib.optionalAttrs (cfg.jwtSecretFile != null) {
                EnvironmentFile = cfg.jwtSecretFile;
              };
            };
          };
        };

      nixosModules.container =
        {
          config,
          lib,
          pkgs,
          ...
        }:
        let
          cfg = config.containers.salus;
        in
        {
          options.containers.salus = {
            enable = lib.mkEnableOption "Salus container (systemd-nspawn)";
            package = lib.mkPackageOption pkgs "salus" { };
            port = lib.mkOption {
              type = lib.types.port;
              default = 8200;
            };
            databaseUrl = lib.mkOption {
              type = lib.types.str;
              default = "sqlite:///var/lib/salus/salus.db";
            };
          };

          config = lib.mkIf cfg.enable {
            containers.salus = {
              autoStart = true;
              privateNetwork = true;
              hostAddress = "10.0.0.1";
              localAddress = "10.0.0.2";

              forwardPorts = [
                {
                  hostPort = cfg.port;
                  containerPort = cfg.port;
                  protocol = "tcp";
                }
              ];

              config = {
                services.salus = {
                  enable = true;
                  inherit (cfg) package port databaseUrl;
                };
              };
            };
          };
        };
    };
}
