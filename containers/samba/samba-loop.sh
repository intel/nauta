#!/bin/bash
sleep 20
SECRETS_DIR=/etc/secrets/samba-users
mkdir -p "$SECRETS_DIR"
LAST_CHECKSUM=`ls -l $SECRETS_DIR | md5sum`

function process_secrets() {
      echo "Secret with user credentials has changed - updating..."
      # kubectl create secret generic prod-db-secret --from-literal=username=produser --from-literal=password=Y4nys7f11
      # filename: {USER_ID}_{GROUP_ID}_{USERNAME}
      # file content: {PASSWORD}
      cd $SECRETS_DIR;
      for f in * ; do
         USER_ID=`echo $f | cut -f1 -d_ `
         GROUP_ID=`echo $f | cut -f2 -d_ `
         USERNAME=`echo $f | cut -f3- -d_ `
         PASSWORD=`cat $f`
         echo "Creating/updating user: $USERNAME (user_$USERNAME)"
         groupadd -g ${GROUP_ID} "group_${USERNAME}"
         echo " -> groupadd -g ${GROUP_ID} group_${USERNAME}  ==> return code: $?"
         adduser --uid ${USER_ID} --gid ${GROUP_ID} "user_${USERNAME}"
         echo " -> adduser --uid ${USER_ID} --gid ${GROUP_ID} user_${USERNAME} ==> return code: $?"
         ( echo ${PASSWORD} ; echo ${PASSWORD}; ) | smbpasswd -a "user_${USERNAME}"
         echo " -> smbpasswd ==> return code: $?"
      done
      cd -
}

for (( ; ; )) ; do
   NEW_CHECKSUM=`ls -l $SECRETS_DIR | md5sum`
   if [[ "x$LAST_CHECKSUM" == "x$NEW_CHECKSUM" ]] ; then
      sleep 5
      echo -n "."
   else
      LAST_CHECKSUM="$NEW_CHECKSUM"
      process_secrets
      echo "Update finished."
   fi
done

