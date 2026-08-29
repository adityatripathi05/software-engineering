"""Lab for 01.8 TLS fundamentals.

Reproduces the incident end-to-end with a real TLS handshake: a three-link
chain (root CA → intermediate → leaf) is generated; the server is started once
serving `cert.pem` (leaf only — the incident's config) and once serving
`fullchain.pem` (leaf + intermediate). A client that trusts only the ROOT — a
strict machine client with no AIA-chasing and no cache, unlike a browser —
fails against the first and succeeds against the second.
"""
import datetime
import socket
import ssl
import threading
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

NOW = datetime.datetime.now(datetime.UTC)


def make_cert(cn: str, issuer_cert, issuer_key, *, is_ca: bool):
    key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    issuer = issuer_cert.subject if issuer_cert is not None else subject
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject).issuer_name(issuer)
        .public_key(key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(NOW - datetime.timedelta(minutes=5))
        .not_valid_after(NOW + datetime.timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=is_ca, path_length=None), critical=True)
    )
    if not is_ca:
        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName(cn)]), critical=False)
    cert = builder.sign(issuer_key if issuer_key is not None else key, hashes.SHA256())
    return cert, key


def pem(cert) -> bytes:
    return cert.public_bytes(serialization.Encoding.PEM)


def serve_once(certfile: str, keyfile: str, port: int) -> threading.Thread:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile, keyfile)

    def run() -> None:
        with socket.create_server(("127.0.0.1", port)) as srv:
            srv.settimeout(5)
            try:
                conn, _ = srv.accept()
                try:
                    ctx.wrap_socket(conn, server_side=True).close()
                except (ssl.SSLError, OSError):
                    pass          # the client aborted the handshake — expected in case 1
            except TimeoutError:
                pass

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t


def try_handshake(port: int, ca_file: str) -> str:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(ca_file)          # trusts the ROOT only, like a clean store
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname="api.ledgerly.com") as tls:
                return f"handshake OK — server cert CN validated, {tls.version()}"
    except ssl.SSLCertVerificationError as e:
        return f"SSLCertVerificationError: {e.verify_message}"


root_cert, root_key = make_cert("Ledgerly Lab Root CA", None, None, is_ca=True)
int_cert, int_key = make_cert("Ledgerly Lab Intermediate", root_cert, root_key, is_ca=True)
leaf_cert, leaf_key = make_cert("api.ledgerly.com", int_cert, int_key, is_ca=False)

with TemporaryDirectory() as d:
    p = Path(d)
    (p / "privkey.pem").write_bytes(leaf_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()))
    (p / "cert.pem").write_bytes(pem(leaf_cert))                       # leaf ONLY
    (p / "fullchain.pem").write_bytes(pem(leaf_cert) + pem(int_cert))  # leaf + intermediate
    (p / "root.pem").write_bytes(pem(root_cert))                       # the client's trust

    print("chain: root CA -> intermediate -> api.ledgerly.com leaf")
    print("client trust store: the ROOT only (a strict machine client)\n")

    t = serve_once(str(p / "cert.pem"), str(p / "privkey.pem"), 8168)
    time.sleep(0.3)
    print("server serves cert.pem      (leaf only):     ", try_handshake(8168, str(p / "root.pem")))
    t.join(timeout=5)

    t = serve_once(str(p / "fullchain.pem"), str(p / "privkey.pem"), 8169)
    time.sleep(0.3)
    print("server serves fullchain.pem (leaf + interm.):", try_handshake(8169, str(p / "root.pem")))
    t.join(timeout=5)

print("\n=> the server must present the intermediates; browsers hide the mistake")
print("   (AIA chasing, cached intermediates) — never validate TLS with a browser (01.8).")
