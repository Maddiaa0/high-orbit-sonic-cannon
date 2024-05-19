# This script will build everything that you need to install the version of noir that you need
# Required Tools
# - cmake + relevant system libraries
# - noirup

# Bootstrap barretenberg - then build the native barretenberg binary
echo "Building bb binary..."
(cd aztec-packages/barretenberg/cpp && cmake --preset clang16 && cmake --build --preset clang16 --target bb)

# Bootstrap noir - We use the latest version with a detatched backend (assumes existence of noirup)
echo "Building noir..."
(cd aztec-packages/noir/noir-repo && noirup -p .)

echo "(If no errors) Bootstrap complete!"