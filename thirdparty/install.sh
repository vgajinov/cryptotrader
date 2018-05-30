for fldr in pydispatch; do
(
   export PYTHONPATH=../../python-modules:$PYTHONPATH
   cd $fldr
   python3 setup.py install --install-lib=../../python-modules
)
done
