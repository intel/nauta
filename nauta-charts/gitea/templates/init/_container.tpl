{{/*
Create helm partial for gitea server
*/}}
{{- define "init" }}
- name: init
  image: {{ required "NAUTA Registry is required" .Values.global.nauta_registry }}/{{ .Values.images.gitea }}
  imagePullPolicy: {{ .Values.images.pullPolicy }}
  env:
  - name: POSTGRES_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ template "db.fullname" . }}
        key: dbPassword
  - name: SCRIPT
    value: &script |-
      mkdir -p /datatmp/gitea/conf
      #if [ ! -f /datatmp/gitea/conf/app.ini ]; then
        sed "s/POSTGRES_PASSWORD/${POSTGRES_PASSWORD}/g" < /etc/gitea/app.ini > /datatmp/gitea/conf/app.ini
      #fi
  command: ["/bin/sh",'-c', *script]
  volumeMounts:
  - name: gitea-data
    mountPath: /datatmp
  - name: gitea-config
    mountPath: /etc/gitea
{{- end }}
