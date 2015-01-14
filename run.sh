# ln resource directory
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [ ! -d $DIR/res ]; then
   echo 'resources file must exist!, please fork conf template from '
   exit;
fi

cd $DIR/res;
git pull origin master;

if [ ! -L $DIR/src/res ]; then
  ln -s $DIR/res $DIR/src/res;
fi

cd $DIR/src/;
python Main.py $@;
