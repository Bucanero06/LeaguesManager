#!/bin/bash

# Ensure the right Python environment is activated (optional but recommended if using virtual environments)
# source /path/to/your/virtualenv/bin/activate

# Generate .rst files
sphinx-apidoc -f -o docs/ src/

# Backup the original index.rst
cp docs/index.rst docs/index.rst.bak

# Create a new index_modules.rst for a clean slate
echo ".. toctree::" >docs/index_modules.rst
echo "   :maxdepth: 2" >>docs/index_modules.rst
echo "   :caption: Modules:" >>docs/index_modules.rst
echo "" >>docs/index_modules.rst

# Extract module names from the generated .rst files and append to index_modules.rst
for file in docs/src.*.rst; do

  # Extract the filename without extension
  module=$(basename $file .rst)
  # Skip unwanted modules, like modules.rst itself
  [[ $module == "src.modules" ]] && continue
  echo "   $module" >>docs/index_modules.rst

  #  # Remove the 'src.' prefix in the .rst files
  #  sed -i 's/.. automodule:: src\./.. automodule:: /g' "$file"
  #  # Adjust the module name for appending to index_modules.rst
  #  module=$(basename $file .rst | sed 's/src.//')

  echo "   $module" >>docs/index_modules.rst

done

# Concatenate the original index.rst and the module list, overwriting the old index.rst
cat docs/index.rst.bak docs/index_modules.rst >docs/index.rst

# Remove temporary files
rm docs/index.rst.bak
rm docs/index_modules.rst

# Build the docs with verbose output for detailed information
cd docs
make clean
make SPHINXOPTS="-v" html
cd ..
