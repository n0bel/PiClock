open(C,"/etc/lirc/lircd.conf");

while(<C>)
{
	if (m/(KEY_[A-Z0-9]+)\s+([0-9a-fx]+)/i)
	{
		$k{$2} = $1;
	}
}
close C;
foreach (sort keys %k)
{
	print $_." ".$k{$_}."\n";
}
open(X,"mode2 -d /dev/lirc0|");
$ps = 0;
$pp = 0;
$bc = 0;
while(<X>)
{
	#print;
	chop;
	($c, $t) = split;
	if ($c eq 'pulse')
	{
		if ($t > 8000) { $b = 0; $bc = 0; $ps = 0; $pp = 0; $lp = $t; next; }
		if ($t > 400 && $t < 700) { $pp = 1; }
	}
	if ($c eq 'space')
	{
		if ($t > 10000) 
		{
			printf("*** %016x %016x %d %d\n",$b,$b^0x00ff00ff,$lp, $ls);
			$s = sprintf("0x%016x",$b);
			if (defined($k{$s}))
			{
				print "********* $k{$s}\n";
			}
		}
		if ($t > 4000) { $b = 0; $bc = 0; $ps = 0; $pp = 0; $ls = $t; next; }
		if ($t > 400 && $t < 700) { $ps = 1; }
		if ($t > 1400 && $t < 1800) { $ps = 2; }
	}
	if ($ps > 0 && $pp > 0)
	{
		$bc++;
		if ($pp == 1 && $ps == 2)
		{
			$b = $b << 1;
			$b = $b | 1;
			#print "*1* $bc\n";
		}
		if ($pp == 1 && $ps == 1)
		{
			$b = $b << 1;
			#print "*0* $bc\n";
		}
		$ps = 0;
		$pp = 0;
	}

}
