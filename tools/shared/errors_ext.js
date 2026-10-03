  /* LEVEL 2 ADDITIONS: friendly messages for errors that first appear in Level 2. */
  ERRORS.KeyError.hints.unshift(
    [/./, "Check the spelling and capital letters of the key. With a dictionary, check first with <code>if key in my_dict:</code> or use <code>my_dict.get(key)</code>. With a pandas table, the key is a column name: <code>print(df.columns)</code> shows the exact names. (The codon table uses capital DNA letters, with T not U.)"]
  );
  ERRORS.ValueError.hints.unshift(
    [/DNA|base|quality|sequence|FASTQ|threshold/i, "If this message comes from a <code>raise ValueError(...)</code> line in your own code, your check did its job: it caught bad input. Read the message, then look at the input you gave the function."]
  );
  ERRORS.AssertionError.hints.unshift(
    [/^AssertionError$/, "This <code>assert</code> has no message, so Python can't say more. Print the values in the condition to see which one is wrong, and consider adding a message: <code>assert x &gt; 0, \"x should be positive\"</code>."],
    [/AssertionError: \S/, "The message above is the one written after the comma in the <code>assert</code> line. It tells you which check failed."]
  );
  ERRORS.PatternError = {
    means: "The regular expression (the pattern you gave the <code>re</code> module) isn't written correctly.",
    hints: [
      [/missing \)|unbalanced parenthesis/, "Every <code>(</code> in a pattern needs a matching <code>)</code>."],
      [/unterminated character set/, "A <code>[</code> was opened but never closed with <code>]</code>."],
      [/nothing to repeat/, "<code>*</code>, <code>+</code> and <code>{n}</code> must come <em>after</em> something to repeat, like <code>A+</code>."],
      [/./, "Write patterns as raw strings, <code>r\"...\"</code>, and build them up one small piece at a time."]
    ]
  };
  ERRORS["re.error"] = ERRORS.PatternError;
  ERRORS.StatisticsError = {
    means: "A function from the <code>statistics</code> module was given data it can't work with, usually an empty list.",
    hints: [[/./, "Check that the list really contains numbers, for example with <code>print(len(values))</code>, before calling <code>mean()</code> or <code>median()</code>."]]
  };
  ERRORS.UnicodeDecodeError = {
    means: "Python tried to read a file as text, but it contains bytes that aren't text in the expected format.",
    hints: [[/./, "Make sure you're opening a text file (such as FASTA, FASTQ, CSV or TSV), not a compressed or binary file."]]
  };
  ERRORS.OSError = {
    means: "Something outside Python went wrong, such as reading a file or reaching a website.",
    hints: [[/./, "If this happened while contacting a website, check your internet connection and try again in a few seconds."]]
  };
