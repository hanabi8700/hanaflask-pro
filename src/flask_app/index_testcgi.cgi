#!/usr/local/bin/perl

# https://hanamaru8700.com/uvblog/src/flask_app/
# 1. ブラウザに「これからHTMLを送ります」と伝えるお約束の行
print "Content-Type: text/html; charset=UTF-8\n\n";

# 2. 表示したいHTMLを出力する
use CGI::Carp qw(fatalsToBrowser);
foreach $key (keys %ENV) {
print "$key --> $ENV{$key}<br>";
}
print <<'HTML';
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>CGIテスト</title>
</head>
<body>
    <h1>こんにちは！CGIです</h1>
    <p>これは index.cgi から出力されたHTMLです。</p>
</body>
</html>
HTML
