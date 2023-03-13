! Program 4
.begin
.org 2048
main: ld [a], %r1
ld [b], %r2
ld [c], %r3
top: subcc %r4, 3, %r0
be done
subcc %r5, %r6, %r0
bneg else
orcc %r1, %r2, %r1
addcc %r6, 1, %r6
ba bottom
else: andcc %r1, %r3, %r1
addcc %r5, 1, %r5
bottom: addcc %r4, 1, %r4
ba top
done: st %r3, [y]
jmpl %r15+4, %r0
.org 3000
a: 0xa0
b: 0x33
c: 0x52
y: 2
.end