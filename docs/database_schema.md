>>Schema

notes:
id              #integer (Primary key)
created_at      #datetime
category        #string
message_body    #text
tag             #string/text
updated_at      #datetime

events:
id              #integer (Primary Key)
note_id         #integer (Foreign Key, apontando para notes.id)
classification  #string/text
scheduled_at    #datetime
status          #string
notification_at #datetime
is_notify       #boolean
