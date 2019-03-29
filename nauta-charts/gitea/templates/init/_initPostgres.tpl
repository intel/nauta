{{/*
Create helm partial for gitea server
*/}}
{{- define "initPostgres" }}
{{ if and (not .Values.useInPodPostgres) (.Values.externalDB) (eq "postgres" .Values.dbType ) }}
- name: init-postgres
  image: "{{ required "NAUTA Registry is required" .Values.global.nauta_registry }}/{{ .Values.images.postgres }}"
  imagePullPolicy: {{ .Values.images.pullPolicy }}
  env:
  - name: PGHOST
    valueFrom:
      secretKeyRef:
        name: {{ template "db.fullname" . }}
        key: dbHost
  - name: PGPORT
    valueFrom:
      secretKeyRef:
        name: {{ template "db.fullname" . }}
        key: dbPort
  - name: DATABASE
    valueFrom:
      secretKeyRef:
        name: {{ template "db.fullname" . }}
        key: dbDatabase
  - name: PGUSER
    valueFrom:
      secretKeyRef:
        name: {{ template "db.fullname" . }}
        key: dbUser
  - name: PGPASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ template "db.fullname" . }}
        key: dbPassword
  - name: POSTGRES_INIT_SCRIPT
    value: &POSTGRES_INIT_SCRIPT |-
      echo "checking postresql for existence of db: $DATABASE";
      DB_EXIST=$(psql -lqt -w | cut -d \| -f 1 | grep ${DATABASE} | sed 's: ::g');
      echo "db exists ${DB_EXIST}:${DATABASE}";
      if [ "${DB_EXIST}" != "${DATABASE}" ]; then
        psql -c "CREATE DATABASE ${DATABASE}";
      else
        echo "existing database detected."
      fi

  command: ["/bin/bash"]
  args: ["-c", *POSTGRES_INIT_SCRIPT]
{{- end }}
{{- end }}
