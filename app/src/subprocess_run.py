import asyncio
from tools import std_out

async def subprocess_run(cmd: str):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    std_out(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        std_out(f'[stdout]\n{stdout.decode()}')
    if stderr:
        std_out(f'[stderr]\n{stderr.decode()}')
