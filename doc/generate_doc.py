#!/usr/bin/env python3
import subprocess
md = subprocess.run(['markdown', 'remcall.md'], check=True, stdout=subprocess.PIPE).stdout.decode('utf8')

print('''<!DOCTYPE HTML>
<html>
<head>
    <title>remcall</title>
    <link rel="stylesheet" href="picnic.min.css">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            max-width: 1200px;
            margin: auto;
            margin-top: 50px;
        }
        .anchor {
            padding-top: 50px;
            margin-top: -50px;
        }
    </style>
</head>
<body>
''')

print(md)

print('''
</body>
</html>
''')
