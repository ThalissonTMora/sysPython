
CREATE TRIGGER notify_api
ON tabela
-- A trigger é acionada após uma inserção ou atualização de uma linha na tabela
AFTER INSERT, UPDATE
AS
BEGIN
  -- Cria uma variável chamada "@json" para armazenar as informações da linha em formato JSON
  DECLARE @json NVARCHAR(MAX) = '';

  -- Cria uma variável chamada @db_name para armazenar o nome do banco de dados.
  DECLARE @db_name NVARCHAR(MAX) = DB_NAME();
  
  -- Obtém as colunas modificadas na tabela
  DECLARE @cols_updated VARBINARY(MAX) = COLUMNS_UPDATED();
  
  -- Verifica se houve modificação em alguma coluna da tabela
  IF @cols_updated > 0
  BEGIN
    -- Adiciona as informações da coluna modificada na variável @json
    SELECT @json = @json + '{"column":"' + COLUMN_NAME + '","old_value":"' + CAST(ISNULL(d.COLUMN_NAME,'') AS VARCHAR(MAX)) + '","new_value":"' + CAST(i.COLUMN_NAME AS VARCHAR(MAX)) + '"}' + ','
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'tabela' AND (POWER(2,ORDINAL_POSITION-1) & @cols_updated) > 0
    
    -- Remove a última vírgula da variável @json
    SET @json = LEFT(@json,LEN(@json)-1)
    
    -- Adiciona os demais campos da linha em formato JSON
    SELECT @json = @json + ',' + campo + ' FROM inserted FOR JSON AUTO';
  END
  ELSE
  BEGIN
    -- Se não houve modificação em nenhuma coluna, adiciona todos os campos da linha em formato JSON
    SELECT @json = campo FROM inserted FOR JSON AUTO;
  END
  
  -- Define o URL da API de notificação e cria um JSON com as informações da notificação a ser enviada
  DECLARE @url VARCHAR(100) = 'http://www.127.0.0.1/api/log/rest'; -- *Link da API (o link usado é um exemplo*)
  DECLARE @body NVARCHAR(MAX) = N'{"banco_de_dados": "' + @db_name + N'", "tabela": "tabela", "tipo": "' + CASE WHEN EXISTS(SELECT * FROM deleted) THEN N'update' ELSE N'insert' ELSE N'delete' END + N'", "dados": ' + @json + N'}';


  -- Cria um objeto WinHttpRequest e faz uma solicitação HTTP POST para a API
  DECLARE @Object AS INT;
  EXEC sp_OACreate 'WinHttp.WinHttpRequest.5.1', @Object OUT;
  EXEC sp_OAMethod @Object, 'Open', NULL, 'POST', @url, 'false';
  EXEC sp_OAMethod @Object, 'SetRequestHeader', null, 'Content-Type', 'application/json';
  EXEC sp_OAMethod @Object, 'Send', NULL, @body;
  EXEC sp_OADestroy @Object;
END;