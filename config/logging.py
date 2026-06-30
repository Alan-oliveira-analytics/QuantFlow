import logging
import re


class RedactApiKey(logging.Filter):
    """Porteiro de segurança: apaga valores de api_key de QUALQUER mensagem de log.

    Funciona para o seu código E para bibliotecas (ex.: urllib3, que loga a URL
    completa — com a key — quando tenta reconectar). Por isso é plugado no
    handler (a porta de saída), não num logger específico.
    """

    _pat = re.compile(r'(api_key=)[^&\s]+')

    def filter(self, record):
        # A key pode estar no "molde" (record.msg)...
        if isinstance(record.msg, str):
            record.msg = self._pat.sub(r'\1*****', record.msg)
        # ...ou nos "valores" (record.args), que é onde libs costumam pôr a URL.
        if record.args:
            record.args = tuple(
                self._pat.sub(r'\1*****', a) if isinstance(a, str) else a
                for a in record.args
            )
        return True  # nunca descarta o log, só higieniza


_CONFIGURED = False


def setup_logging(level=logging.INFO):
    """Configura o logging do projeto UMA vez: formato padrão + redação de segredos.

    Onde chamar: no ENTRYPOINT (quem inicia a execução — o `run()`/`main()` de
    quem é rodado), NÃO nos módulos só importados.

    Idempotente: chamar de novo não duplica handlers nem filtros.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    redactor = RedactApiKey()
    for handler in logging.getLogger().handlers:
        handler.addFilter(redactor)

    _CONFIGURED = True
